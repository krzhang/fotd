import textutils
from textutils import Colors, yprint
import random
import numpy as np
import positions
import skills
from skills import skill_narration
import status
import utils
import insults

# <2019-07-04 Thu> 
# had both statuses and skills here, and decided to offload all skills into statuses, and so
# now only have to think about interplays between statuses and events (as opposed to aslo have)
# skills involved

class Context(object):
  def __init__(self, battle, opt={}):
    self.battle = battle
    self.opt = opt
    for o in opt:
      setattr(self, o, opt[o])

  def copy(self, additional_opt):
    """Make a copy with the same battle context"""
    nopt = self.opt.copy()
    nopt.update(additional_opt)
    return Context(self.battle, opt=nopt)

  def rebase(self, opt):
    """Make a copy with the same battle context"""
    return Context(self.battle, opt=opt)

  def rebase_switch(self):
    """Most common usecase: create a context with switched source/ctargets. """
    return self.rebase({"ctarget":self.csource, "csource":self.ctarget})
  
class EventType(object):
  def __init__(self, inputdict):
    for s in inputdict:
      self.s = inputdict[s]

EVENTS = {}

class Event(object):

  def __init__(self, event_type, context):
    self.event_type = event_type
    self.context = context
      
  def activate(self):
    edict = EVENTS[self.event_type]
    # death handler (should later be "availability" for retreats, etc.)
    if "need_live_actors" in edict and edict["need_live_actors"]:
      if any([not getattr(self.context, foo).is_alive() for foo in edict["actors"]]):
        return
    # panic handler
    if "panic_blocked" in edict and edict["panic_blocked"]:
      potential_panicker = getattr(self.context, edict["primary_actor"])
      if potential_panicker.has_unit_status("panicked"):
        yprint("  %s is %s! No action" % (potential_panicker, status.Status("panicked")))
        return
    # time to activate this event on the queue; note the event has its own context, battle, etc.
    #   Yan has already activated using the tactic fire on Jing
    EVENTS[self.event_type]["func"](self.context)
    # if there is an event func, just run it
    # else:
    #   calculate probability of success
    #     start with base prob
    #     calculate
    #   if successful,

  # def defer(self, event_queue):
  #   """ defer this event to end of turn"""
  #   self.context.battle.gq.appendleft(self)

  @classmethod
  def gain_status(cls, stat_str, context, ctarget):
    """ Basically, nothing should call add_unit_status except for this, so all the handlers are tehre."""
    Event("receive_status", context=context.rebase({"ctarget":ctarget,
                                                    "status":stat_str,
                                                    "stat_viz":str(status.Status(stat_str))})).activate()

  @classmethod
  def remove_status(cls, stat_str, context, ctarget):
    pass

################################
# Utility functions #
################################a

def compute_damage(csource, ctarget, dmg_type, multiplier=1):
  """ We already know who is hitting whom, just computing damage """
  s_str = max(1, csource.attack_strength(dmg_type))
  d_str = max(1, ctarget.defense_strength(dmg_type))
  hitprob = float(s_str) / (d_str + s_str)
  dicecount = int(csource.size*multiplier)
  raw_damage = 0
  for i in range(dicecount):
    roll = random.random()
    if roll < hitprob:
      raw_damage += 1
  damlog = "    [Strength: ({:4.3f} vs. {:4.3f}); {} dice with chance {} each; Final: {}]".format(
    s_str, d_str, dicecount, color_prob(hitprob), color_damage(raw_damage))
  return raw_damage, damlog

################
# Order Events #
################
# after these, there should be a ctarget

def attack_order(context):
  csource = context.ctarget
  if csource.has_unit_status("berserk"):
    Event("berserked_order", context).activate()
    return
  myarmyid = csource.armyid
  enemy = context.battle.armies[1-myarmyid]
  enemyunits = enemy.live_units()
  if len(enemyunits) == 0:
    yprint("No unit to attack!")
    return
  ctarget = random.choice(enemyunits)
  context.ctarget.ctargetting = ctarget
  yprint("{}: marching -> {};".format(csource, ctarget))
  newcontext = context.rebase({"csource":csource, "ctarget":ctarget})
  context.battle.place_event("engage", newcontext, "Q_MANUEVER")

def defense_order(context):
  ctarget = context.ctarget
  if ctarget.has_unit_status("berserk"): # note different dude
    Event("berserked_order", context).activate()
    return
  context.ctarget.ctargetting = None
  ctarget.move(context.battle.hqs[ctarget.armyid])
  yprint("{}: staying put at {};".format(ctarget, context.ctarget.position))
  Event.gain_status("defended", context, ctarget)

def indirect_order(context):
  csource = context.ctarget
  if csource.has_unit_status("berserk"):
    Event("berserked_order", context).activate()
    return
  myarmyid = csource.armyid
  enemy = context.battle.armies[1-myarmyid]
  enemyunits = enemy.live_units()
  if len(enemyunits) == 0:
    yprint("No unit to ctarget!")
    return
  ctarget = random.choice(enemyunits)
  context.ctarget.ctargetting = ctarget
  yprint("{}: sneaking -> {}; planning strategery".format(csource, ctarget))
  newcontext = context.rebase({"csource":csource, "ctarget":ctarget})
  context.battle.place_event("indirect_raid", newcontext, "Q_MANUEVER")

def berserked_order(context):
  csource = context.ctarget
  armyid = random.choice([0,1])
  enemyunits = context.battle.armies[armyid].live_units()
  ctarget = random.choice(enemyunits)
  yprint("{}: random attack -> {}; ignoring orders".format(
    csource, ctarget, status.Status("berserk")))
  context.ctarget.ctargetting = ctarget
  newcontext = context.rebase({"csource":csource, "ctarget":ctarget})
  context.battle.place_event("engage", newcontext, "Q_MANUEVER")
    
EVENTS_ORDERS = {
  "attack_order": {},
  "defense_order": {},
  "indirect_order": {},
  "berserked_order": {}
}

for ev in EVENTS_ORDERS:
  EVENTS_ORDERS[ev]["panic_blocked"] = True
  EVENTS_ORDERS[ev]["actors"] = ["ctarget"]
  EVENTS_ORDERS[ev]["primary_actor"] = "ctarget"
  EVENTS_ORDERS[ev]["need_live_actors"] = True

################
# Generic Battlefield Events #
################

def engage(context):
  csource = context.csource
  ctarget = context.ctarget
  if ctarget in csource.attacked_by:
    yprint("{} was planning to engage {}, but they already engaged".format(csource, ctarget))
    return
  yprint("{} engages {} (-> {})".format(csource, ctarget, ctarget.ctargetting))
  converging = bool(ctarget.ctargetting == csource) # if other ctarget is coming towards you
  if ctarget.is_defended():
    assert ctarget.position == context.battle.hqs[ctarget.armyid] # meeting at hq
    csource.move(ctarget.position)
    yprint("  but %s is ready!" % ctarget)
    yprint("  %s able to launch defensive arrow volley" % ctarget)
    context.battle.place_event("arrow_strike", context.rebase_switch(), "Q_RESOLVE")
    if random.random() < 0.5:    
      yprint("  %s able to launch offensive arrow volley" % csource)
      context.battle.place_event("arrow_strike", context, "Q_RESOLVE")
    context.battle.place_event("physical_clash", context.rebase_switch(), "Q_RESOLVE")
  else:
    newpos = context.battle.make_position(ctarget)
    csource.move(newpos)
    ctarget.move(newpos)
    if random.random() < 0.5:
      yprint("  %s able to launch offensive arrow volley" % csource)
      context.battle.place_event("arrow_strike", context, "Q_RESOLVE")
    # defense doesn't have time to shoot arrows, unless they were coming in this direction
    if converging:
      if random.random() < 0.5:
        yprint("  %s able to launch defensive arrow volley" % ctarget)
        context.battle.place_event("arrow_strike", context.rebase_switch(), "Q_RESOLVE")
    # need logic for when 2 attackers rush into each other
    context.battle.place_event("physical_clash", context, "Q_RESOLVE")

def indirect_raid(context):
  csource = context.csource
  ctarget = context.ctarget
  if len(csource.attacked_by) > 0:
    yprint("{}'s sneaking up on {} was interrupted by {}!".format(csource, ctarget, csource.attacked_by[0]))
    return
  yprint("{} sneaks up on {}".format(csource, ctarget))  
  # tactic 1: raid
  vulnerable = False
  if ctarget.has_unit_status("defended"):
    yprint("  {} is defended against standard attacks but not raids!".format(ctarget))
    vulnerable = True
  context.battle.place_event("arrow_strike",
                             context.copy(additional_opt={"vulnerable":vulnerable}),
                             "Q_RESOLVE")
  # fire
  if (random.random() < 0.4 and
      csource.has_unit_status("fire_tactic") and
      not context.battle.is_raining()):
    context.battle.place_event("fire_tactic", context, "Q_RESOLVE")
  panicprob = 0.20
  if random.random() < panicprob and csource.has_unit_status("panic_tactic"):
    context.battle.place_event("panic_tactic", context, "Q_RESOLVE")
  jeerprob = 0.60
  if random.random() < jeerprob and csource.has_unit_status("jeer"):
    context.battle.place_event("jeer", context, "Q_RESOLVE")
  waterprob = 0.80
  if random.random() < waterprob and csource.has_unit_status("water_tactic") and context.battle.is_raining():
    context.battle.place_event("water_tactic", context, "Q_RESOLVE")

#################
# RESOLVE PHASE #
#################
    
def arrow_strike(context):
  csource = context.csource
  ctarget = context.ctarget
  multiplier = 1
  if "vulnerable" in context.opt and context.vulnerable:
    multiplier = 2
  damage, damlog = compute_damage(csource, ctarget, "DMG_ARROW", multiplier=multiplier)
  dmgstr = "{} shoots {}:".format(csource, ctarget, damage)
  Event("receive_damage",
        context.rebase({"damage":damage, "ctarget":ctarget, "dmgstr":dmgstr, "dmglog":damlog})).activate()
  if csource.has_unit_status("fire_arrow"):
    if random.random() < 0.5 and not context.battle.is_raining():
      skill_narration("fire_arrow", "{}'s arrows are covered with fire!".format(csource), True)
      csource.narrate("Light'em up!")
      Event.gain_status("burned", context, ctarget)
  if csource.has_unit_status("chu_ko_nu"):
    if random.random() < 0.5:
      skill_narration("chu_ko_nu", "{}'s arrows continue to rain!".format(csource), True)
      if csource.name == "Zhuge Liang":
        csource.narrate("The name is a bit embarassing...")
      else:
        csource.narrate("Have some more, guys!")
      Event("arrow_strike", context).activate()
  if ctarget.has_unit_status("counter_arrow"):
    if random.random() < 0.85:
#      yprint("  <counter arrow skill> %s can counter with their own volley of arrows" % ctarget)
      Event("counter_arrow_strike", context.rebase_switch()).activate()

def physical_clash(context):
  csource = context.csource
  ctarget = context.ctarget
  yprint("  {} clashes against {}!".format(csource, ctarget))
  Event("physical_strike", context).activate()
  # yprint("  %s able to launch retaliation" % ctarget) can die in the middle
  Event("physical_strike", context.rebase_switch()).activate()
  
def physical_strike(context):
  """ strike is the singular act of hitting """
  csource = context.csource
  ctarget = context.ctarget
  damage, damlog = compute_damage(csource, ctarget, "DMG_PHYSICAL")
  dmgstr = "{} hits {}:".format(csource, ctarget, damage) 
  # ctarget.add_unit_status("received_physical_attack")
  ctarget.attacked_by.append(csource)
  csource.attacked.append(ctarget)
  Event("receive_damage", context.rebase({"damage":damage, "ctarget":ctarget, "dmgstr":dmgstr, "dmglog":damlog})).activate()

EVENTS_GENERIC_CTARGETTED = {
  "arrow_strike": {},
  "engage": {},
  "indirect_raid": {},
  "physical_clash": {},
  "physical_strike": {}
}

for ev in EVENTS_GENERIC_CTARGETTED:
  EVENTS_GENERIC_CTARGETTED[ev]["panic_blocked"] = True
  EVENTS_GENERIC_CTARGETTED[ev]["actors"] = ["csource", "ctarget"]
  EVENTS_GENERIC_CTARGETTED[ev]["primary_actor"] = "csource"
  EVENTS_GENERIC_CTARGETTED[ev]["need_live_actors"] = True

###############
# MISC EVENTS #
###############

# eventually maybe separate things out with one ctarget unit
  
EVENTS_MISC = {
  # "army_destroyed": {
  #   "actors":["ctarget_army"],
  #   "primary_actor": "ctarget_army"
  # },
  "receive_damage": {
    "actors":["ctarget"],
    "primary_actor": "ctarget",
    "need_live_actors":True
  },
  "receive_status": {
    "actors":["ctarget"],
    "primary_actor": "ctarget",
    "need_live_actors":False # maybe need "Captured" etc.
  }
}

# for ev in EVENTS_RECEIVE:
#   EVENTS_RECEIVE[ev]["panic_blocked"] = True
# No common rules here...

def color_prob(prob):
  pstr = "{:4.3f}".format(prob)
  if prob > 0.75:
    return Colors.GREEN + pstr + Colors.ENDC
  elif prob > 0.5:
    return Colors.MAGENTA + pstr + Colors.ENDC
  elif prob > 0.25:
    return Colors.YELLOW + pstr + Colors.ENDC
  else:
    return Colors.RED + pstr + Colors.ENDC
  
def color_damage(damage):
  if damage == 0:
    return Colors.OKGREEN + str(damage) + Colors.ENDC
  elif damage <= 3:
    return str(damage)
  else:
    return Colors.RED + str(damage) + Colors.ENDC
  
def receive_damage(context):
  ctarget = context.ctarget
  damage = context.damage
  dmgstr = context.dmgstr
  if damage >= ctarget.size:
    damage = ctarget.size
  hpbar = textutils.disp_bar(20, ctarget.size, ctarget.size - damage)
  if dmgstr:
    dmgstr = dmgstr + " "
  fdmgstr = dmgstr + hpbar + " {} -> {} ({} damage)".format(
    ctarget.size,
    ctarget.size - damage,
    color_damage(damage))
  ctarget.size -= damage
  if ctarget.size == 0:
    fdmgstr += "; " + Colors.RED + "DESTROYED!" + Colors.ENDC
  yprint(fdmgstr)
  if context.dmglog:
    yprint(context.dmglog)
  # if not context.battle.armies[ctarget.armyid].is_alive():
  #   Event("army_destroyed", context.rebase({"ctarget_army":ctarget.armyid})).defer()

def receive_status(context):
  ctarget = context.ctarget
  stat_str = context.status
  if "on_receive" in status.STATUSES_BATTLE[stat_str]:
    # sometimes can be quiet
    disp = status.STATUSES_BATTLE[stat_str]["on_receive"].format(**context.opt)
    yprint("  " + disp)
  context.ctarget.add_unit_status(stat_str)
  
######################
# Events from Skills #
######################

def counter_arrow_strike(context):
  csource = context.csource
  ctarget = context.ctarget
  skill_narration("counter_arrow", "{} counters with their own volley".format(csource), True)
  csource.narrate("Come on boys; let's show these guys how to actually use arrows!")
  Event("arrow_strike",
        context.rebase({"csource":csource, "ctarget":ctarget})).activate()

def fire_tactic(context):
  csource = context.csource
  ctarget = context.ctarget
  success = random.random() < 0.5
  skill_narration("fire_tactic",
                  "{} prepares embers and tinder...".format(csource))
  if success:
    csource.narrate("It's going to get pretty hot!")
    Event.gain_status("burned", context, ctarget)
  else:
    ctarget.narrate("No need to play with fire, boys. Fight like real men!")
  skill_narration("fire_tactic", "", success)

def jeer(context):
  csource = context.csource
  ctarget = context.ctarget
  # should interrupt this, but right now it should be fine
  success = random.random() < 0.3
  skill_narration("jeer",
                  "{} prepares their best insults...".format(csource))
  ins = random.choice(insults.INSULTS)
  csource.narrate(ins[0])
  if success:
    ctarget.narrate("Why you...")
    Event.gain_status("berserk", context, ctarget)
  else:
    ctarget.narrate(ins[1])  
  skill_narration("jeer", "", success)
    
def panic_tactic(context):
  csource = context.csource
  ctarget = context.ctarget  
  # if csource.has_unit_status("panicked"):
  #   # you need this here anyway because maybe a unit got panicked right before considering a tactic
  #   yprint("  %s is panicked (ironically)! No action" % csource)
  #   return
  success = random.random() < 0.5
  skill_narration("panic_tactic",
                  "{} sows seeds of chaos in {}'s unit...".format(csource, ctarget))
  if success:
    csource.narrate("{} will be out of commission for a while...".format(ctarget))
    Event.gain_status("panicked", context, ctarget)
  else:
    ctarget.narrate("Keep calm. Don't let {}'s trickery get to you.".format(csource))
  skill_narration("panic_tactic", "", success)

def water_tactic(context):
  csource = context.csource
  ctarget = context.ctarget  
  success = random.random() < 0.5
  skill_narration("water_tactic",
                  "{} positions dams and ships...".format(csource, ctarget))
  if success:
    damdice = 12
    damage = random.choice(range(damdice))
    dmgstr = "{}'s unit is flooded by a torrent, aggravated by the pouring {}".format(ctarget, context.battle.weather)
    Event("receive_damage", context.copy(
      additional_opt={"damage":damage, "dmgstr":dmgstr, "dmglog":""})).activate()
    csource.narrate("This is painful to look at...")
  else:
    ctarget.narrate("We narrowly avoided being swept away. Water is a very scary force of nature!")
  skill_narration("water_tactic", "", success)
  
  
EVENTS_SKILLS = {
  "counter_arrow_strike": {},
  "fire_tactic": {},
  "jeer": {},
  "panic_tactic": {},
  "water_tactic": {}
}

for ev in EVENTS_SKILLS:
  EVENTS_SKILLS[ev]["panic_blocked"] = True
  EVENTS_SKILLS[ev]["actors"] = ["csource", "ctarget"]
  EVENTS_SKILLS[ev]["primary_actor"] = "csource"
  EVENTS_SKILLS[ev]["need_live_actors"] = True


EVENTS = dict(list(EVENTS_ORDERS.items()) +
              list(EVENTS_GENERIC_CTARGETTED.items()) +
              list(EVENTS_MISC.items()) +
              list(EVENTS_SKILLS.items()))

#######################################
# Status Beginning/end of turn Events #
#######################################

# Strictly speaking, these aren't events right now, since we just run them. This means we can activate but cannot defer

def generic_eot_fizzle(context):
  # a bit annoying that removal is not symmetric with gaining
  stat_str = context.status
  if status.info(stat_str, "on_remove") != "":
    # eventually, maybe do specialized stuff
    yprint("{} is no longer {}".format(context.ctarget, status.Status(stat_str)))
  context.ctarget.remove_unit_status(stat_str)
  
def burned_bot(context):
  ctarget = context.ctarget
  if context.battle.is_raining():
    yprint("thanks to the rain, %s put out the fire." % ctarget)
    ctarget.remove_unit_status("burned")
  
def burned_eot(context):
  ctarget = context.ctarget
  if ctarget.has_unit_status("burned"): # could have dried up or something
    # damage before putting out
    if context.battle.is_hot():
      damdice = 10
      yprint("It's an extra {} day; fire is much more dangerous.".format(context.battle.weather))
    else:
      damdice = 5
    damage = random.choice(range(damdice))
    dmgstr = "{}'s unit is {}".format(ctarget, status.Status("burned"))
    Event("receive_damage", context.copy(
      additional_opt={"damage":damage, "dmgstr":dmgstr, "dmglog":""})).activate()
    if random.random() < 0.5:
      yprint("s put out the fire." % ctarget)
      ctarget.remove_unit_status("burned")
    else:
      yprint("The fire burning %s rages on." % ctarget)

def berserk_eot(context):
  ctarget = context.ctarget
  if ctarget.has_unit_status("berserk"): # could have dried up or something
    if random.random() < 0.5:
      yprint("%s regains control." % ctarget)
      ctarget.remove_unit_status("berserk")
    else:
      yprint("{}'s unit is still {}.".format(ctarget, status.Status("berserk")))

def panic_eot(context):
  ctarget = context.ctarget
  if ctarget.has_unit_status("panicked"): # could have dried up or something
    if random.random() < 0.5:
      yprint("%s regains control." % ctarget)
      ctarget.remove_unit_status("panicked")
    else:
      yprint("%s's unit is still panicking." % ctarget)

##########
# Skills #
##########

def trymode_status_bot(context):
  ctarget = context.ctarget
  trymodeprob = (20.0-ctarget.size)/20
  success = random.random() < trymodeprob
  skill_narration("trymode", "{} looks for an excuse to pretend to be powered up...".format(ctarget))
  if success:
    ctarget.narrate("Did you really think I took you seriously before?")
    Event.gain_status("trymode_activated", context, ctarget) 
  else:
    ctarget.narrate("I have not tried yet, and I still do not need to.")
  skill_narration("trymode", "", success)

