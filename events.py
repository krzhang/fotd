import textutils
from textutils import Colors, yprint
import random
import numpy as np
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
    """Most common usecase: create a context with switched source/targets. """
    return self.rebase({"target":self.source, "source":self.target})
  
  def add_event(self, event):
    self.battle.gq.put(event)
  
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
    
  def defer(self):
    """ defer this event to end of turn"""
    self.context.battle.gq.appendleft(self)

  @classmethod
  def gain_status(cls, stat_str, context, target):
    Event("receive_status", context=context.rebase({"target":target,
                                                    "status":stat_str,
                                                    "stat_viz":str(status.Status(stat_str))})).activate()

################################
# Utility functions #
################################a

def compute_damage(source, target, dmg_type, multiplier=1):
  """ We already know who is hitting whom, just computing damage """
  s_str = max(1, source.attack_strength(dmg_type))
  d_str = max(1, target.defense_strength(dmg_type))
  hitprob = float(s_str) / (d_str + s_str)
  dicecount = int(s_str*multiplier)
  raw_damage = 0
  for i in range(dicecount):
    roll = random.random()
    if roll < hitprob:
      raw_damage += 1
  damlog = "    [Strength: ({4.3f} vs. {4.3f}); {} dice with chance {} each; Final: {}]".format(
    s_str, d_str, dicecount, color_prob(hitprob), color_damage(raw_damage))
  return raw_damage, damlog

################
# Order Events #
################
# after these, there should be a target

def attack_order(context):
  source = context.target
  if source.has_unit_status("berserk"):
    Event("berserked_order", context).activate()
    return
  myarmyid = source.armyid
  enemy = context.battle.armies[1-myarmyid]
  enemyunits = enemy.live_units()
  if len(enemyunits) == 0:
    yprint("No unit to attack!")
    return
  target = random.choice(enemyunits)
  context.target.targetting = target
  yprint("{}: marching -> {};".format(source, target))
  Event("engage", context.rebase({"source":source, "target":target})).defer()

def defense_order(context):
  target = context.target
  if target.has_unit_status("berserk"): # note different dude
    Event("berserked_order", context).activate()
    return
  context.target.targetting = None
  yprint("{}: staying put;".format(target))
  Event.gain_status("defended", context, target)

def indirect_order(context):
  source = context.target
  if source.has_unit_status("berserk"):
    Event("berserked_order", context).activate()
    return
  myarmyid = source.armyid
  enemy = context.battle.armies[1-myarmyid]
  enemyunits = enemy.live_units()
  if len(enemyunits) == 0:
    yprint("No unit to target!")
    return
  target = random.choice(enemyunits)
  context.target.targetting = target
  yprint("{}: sneaking -> {}; planning strategery".format(source, target))
  Event("indirect_raid", context.rebase({"source":source, "target":target})).defer()

def berserked_order(context):
  source = context.target
  armyid = random.choice([0,1])
  enemyunits = context.battle.armies[armyid].live_units()
  target = random.choice(enemyunits)
  yprint("{}: random attack -> {}; ignoring orders".format(
    source, target, status.Status("berserk")))
  context.target.targetting = target
  Event("engage", context.rebase({"source":source, "target":target})).defer()
    
EVENTS_ORDERS = {
  "attack_order": {},
  "defense_order": {},
  "indirect_order": {},
  "berserked_order": {}
}

for ev in EVENTS_ORDERS:
  EVENTS_ORDERS[ev]["panic_blocked"] = True
  EVENTS_ORDERS[ev]["actors"] = ["target"]
  EVENTS_ORDERS[ev]["primary_actor"] = "target"
  EVENTS_ORDERS[ev]["need_live_actors"] = True

################
# Generic Battlefield Events #
################

def engage(context):
  source = context.source
  target = context.target
  if target in source.attacked_by:
    yprint("{} was planning to engage {}, but they already engaged".format(source, target))
    return
  yprint("{} engages {} (-> {})".format(source, target, target.targetting))  
  if target.is_defended():
    yprint("  but %s is ready!" % target)
    yprint("  %s able to launch defensive arrow volley" % target)
    Event("arrow_strike", context.rebase_switch()).activate()
    if random.random() < 0.5:    
      yprint("  %s able to launch offensive arrow volley" % source)
      Event("arrow_strike", context).activate()
    Event("physical_clash", context.rebase_switch()).activate()
  else:
    if random.random() < 0.5:
      yprint("  %s able to launch offensive arrow volley" % source)
      Event("arrow_strike", context).activate()
    # defense doesn't have time to shoot arrows, unless they were coming in this direction
    if target.targetting == source:
      if random.random() < 0.5:
        yprint("  %s able to launch defensive arrow volley" % target)
        Event("arrow_strike", context.rebase_switch()).activate()      
    # need logic for when 2 attackers rush into each other
    Event("physical_clash", context).activate()

def indirect_raid(context):
  source = context.source
  target = context.target
  if len(source.attacked_by) > 0:
    yprint("{}'s sneaking up on {} was interrupted by {}!".format(source, target, source.attacked_by[0]))
    return
  yprint("{} sneaks up on {}".format(source, target))  
  # tactic 1: raid
  vulnerable = False
  if target.has_unit_status("defended"):
    yprint("  {} is defended against standard attacks but not raids!".format(target))
    vulnerable = True
  Event("arrow_strike", context.copy(additional_opt={"vulnerable":vulnerable})).activate()
  # fire
  if (random.random() < 0.4 and
      source.has_unit_status("fire_tactic") and
      not context.battle.is_raining()):
    Event("fire_tactic", context).activate()
  panicprob = 0.20
  if random.random() < panicprob and source.has_unit_status("panic_tactic"):
    Event("panic_tactic", context).activate()
  jeerprob = 0.60
  if random.random() < jeerprob and source.has_unit_status("jeer"):
    Event("jeer", context).activate()
    
def arrow_strike(context):
  source = context.source
  target = context.target
  multiplier = 1
  if "vulnerable" in context.opt and context.vulnerable:
    multiplier = 2
  damage, damlog = compute_damage(source, target, "DMG_ARROW", multiplier=multiplier)
  dmgstr = "{} shoots {}:".format(source, target, damage)
  Event("receive_damage",
        context.rebase({"damage":damage, "target":target, "dmgstr":dmgstr, "dmglog":damlog})).activate()
  if source.has_unit_status("fire_arrow"):
    if random.random() < 0.5 and not context.battle.is_raining():
      skill_narration("fire_arrow", "{}'s arrows are covered with fire!".format(source), True)
      source.narrate("Light'em up!")
      Event.gain_status("burned", context, target)
  if source.has_unit_status("chu_ko_nu"):
    if random.random() < 0.5:
      skill_narration("chu_ko_nu", "{}'s arrows continue to rain!".format(source), True)
      if source.name == "Zhuge Liang":
        source.narrate("It's a bit embarassing to be using something named after yourself...")
      else:
        source.narrate("Have some more, guys!")
      Event("arrow_strike", context).activate()
  if target.has_unit_status("counter_arrow"):
    if random.random() < 0.85:
#      yprint("  <counter arrow skill> %s can counter with their own volley of arrows" % target)
      Event("counter_arrow_strike", context.rebase_switch()).activate()

def physical_clash(context):
  source = context.source
  target = context.target
  yprint("  {} clashes against {}!".format(source, target))
  Event("physical_strike", context).activate()
  # yprint("  %s able to launch retaliation" % target) can die in the middle
  Event("physical_strike", context.rebase_switch()).activate()
  
def physical_strike(context):
  """ strike is the singular act of hitting """
  source = context.source
  target = context.target
  damage, damlog = compute_damage(source, target, "DMG_PHYSICAL")
  dmgstr = "{} hits {}:".format(source, target, damage) 
  target.add_unit_status("received_physical_attack")
  target.attacked_by.append(source)
  source.attacked.append(target)
  Event("receive_damage", context.rebase({"damage":damage, "target":target, "dmgstr":dmgstr, "dmglog":damlog})).activate()

EVENTS_GENERIC_TARGETTED = {
  "arrow_strike": {},
  "engage": {},
  "indirect_raid": {},
  "physical_clash": {},
  "physical_strike": {}
}

for ev in EVENTS_GENERIC_TARGETTED:
  EVENTS_GENERIC_TARGETTED[ev]["panic_blocked"] = True
  EVENTS_GENERIC_TARGETTED[ev]["actors"] = ["source", "target"]
  EVENTS_GENERIC_TARGETTED[ev]["primary_actor"] = "source"
  EVENTS_GENERIC_TARGETTED[ev]["need_live_actors"] = True

###############
# MISC EVENTS #
###############

# eventually maybe separate things out with one target unit
  
EVENTS_MISC = {
  "army_destroyed": {
    "actors":["target_army"],
    "primary_actor": "target_army"
  },
  "receive_damage": {
    "actors":["target"],
    "primary_actor": "target",
    "need_live_actors":True
  },
  "receive_status": {
    "actors":["target"],
    "primary_actor": "target",
    "need_live_actors":False # maybe need "Captured" etc.
  }
}

# for ev in EVENTS_RECEIVE:
#   EVENTS_RECEIVE[ev]["panic_blocked"] = True
# No common rules here...

def army_destroyed(context):
  yprint("Army %d loses the battle" % context.target_army)

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
    return Colors.GREEN + str(damage) + Colors.ENDC
  elif damage <= 3:
    return str(damage)
  else:
    return Colors.RED + str(damage) + Colors.ENDC
  
def receive_damage(context):
  target = context.target
  damage = context.damage
  dmgstr = context.dmgstr
  if damage >= target.size:
    damage = target.size
  hpbar = textutils.disp_bar(20, target.size, target.size - damage)
  fdmgstr = "  {} ".format(dmgstr) + hpbar + " {} -> {} ({} damage)".format(
    target.size,
    target.size - damage,
    color_damage(damage))
  target.size -= damage
  if target.size == 0:
    fdmgstr += "; " + Colors.RED + "DESTROYED!" + Colors.ENDC
  yprint(fdmgstr)
  yprint(context.dmglog)
  if not context.battle.armies[target.armyid].is_alive():
    Event("army_destroyed", context.rebase({"target_army":target.armyid})).defer()

def receive_status(context):
  target = context.target
  stat_str = context.status
  if "on_receive" in status.STATUSES_BATTLE[stat_str]:
    # sometimes can be quiet
    disp = status.STATUSES_BATTLE[stat_str]["on_receive"].format(**context.opt)
    yprint("  " + disp)
  context.target.add_unit_status(stat_str)
  
######################
# Events from Skills #
######################

def counter_arrow_strike(context):
  source = context.source
  target = context.target
  skill_narration("counter_arrow", "{} counters with their own volley".format(source), True)
  source.narrate("Come on boys; let's show these guys how to actually use arrows!")
  Event("arrow_strike",
        context.rebase({"source":source, "target":target})).activate()

def fire_tactic(context):
  source = context.source
  target = context.target
  success = random.random() < 0.5
  skill_narration("fire_tactic",
                  "{} prepares embers and tinder...".format(source))
  if success:
    source.narrate("It's going to get pretty hot!")
    Event.gain_status("burned", context, target)
  else:
    target.narrate("No need to play with fire, boys. Fight like real men!")
  skill_narration("fire_tactic", "", success)

def jeer(context):
  source = context.source
  target = context.target
  # should interrupt this, but right now it should be fine
  success = random.random() < 0.3
  skill_narration("jeer",
                  "{} prepares their best insults...".format(source))
  ins = random.choice(insults.INSULTS)
  source.narrate(ins[0])
  if success:
    target.narrate("Why you...")
    Event.gain_status("berserk", context, target)
  else:
    target.narrate(ins[1])  
  skill_narration("jeer_tactic", "", success)
    
def panic_tactic(context):
  source = context.source
  target = context.target  
  # if source.has_unit_status("panicked"):
  #   # you need this here anyway because maybe a unit got panicked right before considering a tactic
  #   yprint("  %s is panicked (ironically)! No action" % source)
  #   return
  success = random.random() < 0.5
  skill_narration("panic_tactic",
                  "{} sows seeds of chaos in {}'s unit...".format(source, target))
  if success:
    source.narrate("{} will be out of commission for a while...".format(target))
    Event.gain_status("panicked", context, target)
  else:
    target.narrate("Keep calm. Don't let {}'s trickery get to you.".format(source))
  skill_narration("panic_tactic", "", success)

EVENTS_SKILLS = {
  "counter_arrow_strike": {},
  "fire_tactic": {},
  "jeer": {},
  "panic_tactic": {}
}

for ev in EVENTS_SKILLS:
  EVENTS_SKILLS[ev]["panic_blocked"] = True
  EVENTS_SKILLS[ev]["actors"] = ["source", "target"]
  EVENTS_SKILLS[ev]["primary_actor"] = "source"
  EVENTS_SKILLS[ev]["need_live_actors"] = True


EVENTS = dict(list(EVENTS_ORDERS.items()) +
              list(EVENTS_GENERIC_TARGETTED.items()) +
              list(EVENTS_MISC.items()) +
              list(EVENTS_SKILLS.items()))

#######################################
# Status Beginning/end of turn Events #
#######################################

# Strictly speaking, these aren't events right now, since we just run them. This means we can activate but cannot defer

def generic_eot_fizzle(context):
  # a bit annoying that removal is not symmetric with gaining
  stat_str = context.status
  if status.STATUSES[stat_str]["on_remove"] != "":
    # eventually, maybe do specialized stuff
    yprint("{} is no longer {}".format(context.target, status.Status(stat_str)))
  context.target.remove_unit_status(stat_str)
  
def burned_bot(context):
  target = context.target
  if context.battle.is_raining():
    yprint("hanks to the rain, %s put out the fire." % target)
    target.remove_unit_status("burned")
  
def burned_eot(context):
  target = context.target
  if target.has_unit_status("burned"): # could have dried up or something
    # damage before putting out
    if context.battle.is_hot():
      damdice = 10
      yprint("It's an extra {} day; fire is much more dangerous.".format(context.battle.weather))
    else:
      damdice = 5
    damage = random.choice(range(damdice))
    dmgstr = "{}'s unit is {}".format(target, status.Status("burned"))
    Event("receive_damage", context.copy(
      additional_opt={"target":target, "damage":damage, "dmgstr":dmgstr})).activate()
    if random.random() < 0.5:
      yprint("s put out the fire." % target)
      target.remove_unit_status("burned")
    else:
      yprint("The fire burning %s rages on." % target)

def berserk_eot(context):
  target = context.target
  if target.has_unit_status("berserk"): # could have dried up or something
    if random.random() < 0.5:
      yprint("%s regains control." % target)
      target.remove_unit_status("berserk")
    else:
      yprint("{}'s unit is still {}.".format(target, status.Status("berserk")))

def panic_eot(context):
  target = context.target
  if target.has_unit_status("panicked"): # could have dried up or something
    if random.random() < 0.5:
      yprint("%s regains control." % target)
      target.remove_unit_status("panicked")
    else:
      yprint("%s's unit is still panicking." % target)

##########
# Skills #
##########

def trymode_status_bot(context):
  target = context.target
  trymodeprob = (20.0-target.size)/20
  success = random.random() < trymodeprob
  skill_narration("trymode", "{} looks for an excuse to pretend to be powered up...".format(target))
  if success:
    target.narrate("Did you really think I took you seriously before?")
    target.add_unit_status("trymode_activated") 
  else:
    target.narrate("I have not tried yet, and I still do not need to.")
  skill_narration("trymode", "", success)

