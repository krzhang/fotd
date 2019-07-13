import random

import battle_constants
import duel
import rps
import skills
import status
import insults
import textutils

# <2019-07-04 Thu>
# had both statuses and skills here, and decided to offload all skills into statuses, and so
# now only have to think about interplays between statuses and events (as opposed to aslo have)
# skills involved

EVENTS = {}

class Event():

  def __init__(self, event_name, context):
    self.event_name = event_name
    self.context = context

  def activate(self):
    edict = EVENTS[self.event_name]
    # death handler (should later be "availability" for retreats, etc.)
    # most events require actors who are alive
    if ("allow_non_present_actors" not in edict) or not edict["allow_non_present_actors"]:
      if any([not self.context.opt[foo].is_present() for foo in edict["actors"]]): #pylint:disable=blacklisted-name
        return
    # berserk handler on orders
    if self.event_name in ["attack_order", "defense_order", "indirect_order"]:
      ctarget = self.context.ctarget
      if ctarget.has_unit_status("berserk"):
        Event("berserked_order", self.context).activate()
        return
    # panic handler
    if event_info(self.event_name, "panic_blocked"):
      potential_panicker = getattr(self.context, edict["primary_actor"])
      if potential_panicker.has_unit_status("panicked"):
        self.context.battle.battlescreen.yprint("  %s is %s! No action" % (potential_panicker, status.Status("panicked")))
        return
    # time to activate this event on the queue; note the event has its own context, battle, etc.
    results = run_event_func(self.event_name, self.context, self.context.battle.battlescreen)

  @classmethod
  def gain_status(cls, stat_str, context, ctarget):
    """
    Basically, nothing should call add_unit_status except for this, so all the handlers are there.
    """
    Event("receive_status", context=context.rebase({"ctarget":ctarget,
                                                    "status":stat_str,
                                                    "stat_viz":str(status.Status(stat_str))})).activate()

  @classmethod
  def make_speech(cls, unit, context, speech):
    newspeech = speech.format(**context.opt)
    context.battle.narrator.unit_speech(unit, newspeech)
    # Event("make_speech", context=context.copy(additional_opt={"ctarget":unit,
    #                                                           "speech":newspeech})).activate()

  @classmethod
  def remove_status(cls, stat_str, context, ctarget):
    pass


def event_dict(event_name):
  return EVENTS[event_name]

def event_info(event_name, key):
  """ Main auxilary function; gets a piece of info about an event type, and None otherwise."""
  edict = event_dict(event_name)
  if key in edict:
    return edict[key]
  return None

def run_event_func(event_name, context, battlescreen, **kwargs):
  """
  runs one of the event functions in this section by name, giving a context 
  and a view (battlescreen)
  """
  return globals()[event_name](context, context.battle.battlescreen, **kwargs)

################################
# Utility functions #
################################a

def _roll_dice(s_str, d_str, dicecount):
  if d_str + s_str < 0.00001: # to avoid dividing by 0
    return 0
  hitprob = float(s_str) / (d_str + s_str)
  raw_damage = 0
  for _ in range(dicecount):
    roll = random.random()
    if roll < hitprob:
      raw_damage += 1
  return raw_damage, hitprob

def _compute_physical_damage(csource, ctarget, multiplier=1):
  """ We already know who is hitting whom, just computing damage """
  s_str = csource.physical_offense()
  d_str = ctarget.physical_defense()
  dicecount = int(csource.size*multiplier)
  # this is the data needed to create a log of the damage later; for timing purposes this needs
  raw_damage, hitprob = _roll_dice(s_str, d_str, dicecount)
  dmglog = tuple((s_str, d_str, dicecount, hitprob, raw_damage))
  # we pass this on instead of printing it immediately, both for MVC purposes and because
  # it's weird for the user to see damage computed first before seeing damage done on screen
  return raw_damage, dmglog

def _compute_arrow_damage(csource, ctarget, multiplier=1):
  """ We already know who is hitting whom, just computing damage """
  s_str = csource.arrow_offense()
  d_str = ctarget.arrow_defense()
  if ctarget.is_defended():
    d_str *= 1.5
  dicecount = int(csource.size*multiplier)
  raw_damage, hitprob = _roll_dice(s_str, d_str, dicecount)
  dmglog = tuple((s_str, d_str, dicecount, hitprob, raw_damage))
  return raw_damage, dmglog

################
# Order Events #
################
# after these, there should be a ctarget

def attack_order(context, bv, **kwargs):
  ctarget = context.ctarget
  myarmyid = ctarget.army.armyid
  enemy = context.battle.armies[1-myarmyid]
  enemyunits = enemy.present_units()
  if not enemyunits:
    bv.yprint("No unit to attack!")
    return
  cnewsource = context.ctarget # new event
  cnewtarget = random.choice(enemyunits)
  cnewsource.ctargetting = ("marching", cnewtarget)
  bv.yprint("{}: marching -> {};".format(cnewsource, cnewtarget), debug=True)
  newcontext = context.rebase({"csource":cnewsource, "ctarget":cnewtarget})
  context.battle.place_event("march", newcontext, "Q_MANUEVER")

def defense_order(context, bv, **kwargs):
  ctarget = context.ctarget
  ctarget.ctargetting = ("defending", ctarget)
  ctarget.move(context.battle.hqs[ctarget.army.armyid])
  bv.yprint("{}: staying put at {};".format(ctarget, context.ctarget.position), debug=True)
  Event.gain_status("defended", context, ctarget)

def indirect_order(context, bv, **kwargs):
  csource = context.ctarget
  myarmyid = csource.army.armyid
  enemy = context.battle.armies[1-myarmyid]
  enemyunits = enemy.present_units()
  if not enemyunits:
    bv.yprint("No unit to target!")
    return
  cnewsource = context.ctarget # new event
  cnewtarget = random.choice(enemyunits)
  cnewsource.ctargetting = ("sneaking", cnewtarget)
  bv.yprint("{}: sneaking -> {}; planning strategery".format(cnewsource, cnewtarget), debug=True)
  newcontext = context.rebase({"csource":cnewsource, "ctarget":cnewtarget})
  context.battle.place_event("indirect_raid", newcontext, "Q_MANUEVER")

def berserked_order(context, bv, **kwargs):
  csource = context.ctarget
  armyid = random.choice([0, 1])
  enemyunits = context.battle.armies[armyid].present_units()
  ctarget = random.choice(enemyunits)
  bv.yprint("{}: random {} attack -> {}; ignoring original orders".format(
    csource, status.Status("berserk"), ctarget))
  context.ctarget.ctargetting = ("marching", ctarget)
  newcontext = context.rebase({"csource":csource, "ctarget":ctarget})
  context.battle.place_event("march", newcontext, "Q_MANUEVER")

def provoked_order(context, bv, **kwargs):
  csource = context.ctarget
  armyid = context.ctarget.army.armyid
  enemyunits = context.battle.armies[armyid].present_units()
  ctarget = random.choice(enemyunits)
  bv.yprint("{}: random {} attack -> {}; ignoring original orders".format(
    csource, status.Status("provoked"), ctarget))
  context.ctarget.ctargetting = ("marching", ctarget)
  newcontext = context.rebase({"csource":csource, "ctarget":ctarget})
  context.battle.place_event("march", newcontext, "Q_MANUEVER")

EVENTS_ORDERS = {
  "attack_order": {},
  "defense_order": {},
  "indirect_order": {},
  "berserked_order": {},
  "provoked_order": {}
}

for ev in EVENTS_ORDERS:
  EVENTS_ORDERS[ev]["panic_blocked"] = True
  EVENTS_ORDERS[ev]["actors"] = ["ctarget"]
  EVENTS_ORDERS[ev]["primary_actor"] = "ctarget"

################
# Generic Battlefield Events #
################

def march(context, bv, **kwargs):
  csource = context.csource
  ctarget = context.ctarget
  if ctarget in csource.attacked_by:
    bv.yprint("{} already engaged {}, but they already engaged".format(csource, ctarget), debug=True)
    return
  if ctarget.is_defended():
    readytext = "$[2]$defended!$[7]$"
  else:
    readytext = textutils.disp_unit_ctargetting(ctarget)
  bv.yprint("{} ({}) marches into {} ({})".format(csource,
                                                      textutils.disp_unit_ctargetting(csource),
                                                      ctarget,
                                                      readytext))
  if ctarget.is_defended():
    Event("engage", context.rebase_switch()).activate()
  else:
    Event("engage", context).activate()
  
  converging = bool(ctarget.ctargetting[1] == csource) # if other ctarget is coming towards you
  if ctarget.is_defended():
    assert ctarget.position == context.battle.hqs[ctarget.army.armyid] # meeting at hq
    csource.move(ctarget.position)
    bv.yprint("  %s able to launch defensive arrow volley" % ctarget, debug=True)
    context.battle.place_event("arrow_strike", context.rebase_switch(), "Q_RESOLVE")
    if random.random() < 0.5:
      bv.yprint("  %s able to launch offensive arrow volley" % csource, debug=True)
      context.battle.place_event("arrow_strike", context, "Q_RESOLVE")
    context.battle.place_event("physical_clash", context.rebase_switch(), "Q_RESOLVE")
  else:
    newpos = context.battle.make_position(ctarget)
    csource.move(newpos)
    ctarget.move(newpos)
    if random.random() < 0.5:
      bv.yprint("  %s able to launch offensive arrow volley" % csource, debug=True)
      context.battle.place_event("arrow_strike", context, "Q_RESOLVE")
    # defense doesn't have time to shoot arrows, unless they were coming in this direction
    if converging:
      if random.random() < 0.5:
        bv.yprint("  %s able to launch defensive arrow volley" % ctarget, debug=True)
        context.battle.place_event("arrow_strike", context.rebase_switch(), "Q_RESOLVE")
    # need logic for when 2 attackers rush into each other
    context.battle.place_event("physical_clash", context, "Q_RESOLVE")

def indirect_raid(context, bv, **kwargs):
  csource = context.csource
  ctarget = context.ctarget
  if csource.attacked_by:
    bv.yprint("{}'s sneaking up on {} was interrupted by {}!".format(csource, ctarget, csource.attacked_by[0]))
    return
  bv.yprint("{} ({}) sneaks up on {} ({})".format(csource,
                                                         textutils.disp_unit_ctargetting(csource),
                                                         ctarget,
                                                         textutils.disp_unit_ctargetting(ctarget)))
  context.battle.place_event("duel_consider", context, "Q_RESOLVE")
  # tactic 1: raid
  vulnerable = False
  if ctarget.ctargetting[0] == "defending":
    bv.yprint("  {} is caught unawares by the indirect approach!".format(ctarget), debug=True)
    vulnerable = True
  elif ctarget.ctargetting[0] == "marching":
    bv.yprint("  {}'s marching soldiers are vigilant!".format(ctarget), debug=True)
  context.battle.place_event("arrow_strike",
                             context.copy(additional_opt={"vulnerable":vulnerable}),
                             "Q_RESOLVE")

def engage(context, bv, **kwargs):
  """
  What happens when they meet face to face, but before the attacks. All the resolved tactics
  fire off. Tactics only fire when they have yomi advantage.
  """
  csource = context.csource
  ctarget = context.ctarget
  army = csource.army
  for sc in army.tableau.bulbed_by(csource):
    context.battle.place_event(sc.sc_str, context, "Q_RESOLVE")
  context.battle.place_event("duel_consider", context, "Q_RESOLVE")

#################
# RESOLVE PHASE #
#################

def duel_accepted(context, bv, **kwargs):
  csource = context.csource
  ctarget = context.ctarget
  actors = [csource, ctarget]
  healths = [20, 20]
  health_history = [(20, 20)]
  loser_history = [None]
  damage_history = []
  while (healths[0] > 0 and healths[1] > 0):
    first_win = random.random() < csource.character.power/(ctarget.character.power + csource.character.power)
    if first_win:
      loser = 1
    else:
      loser = 0
    loser_history.append(loser)
    damage = random.randint(1, 3)
    healths[loser] -= damage
    damage_history.append(damage)
    health_history.append(tuple(healths))
  bv.disp_duel(csource, ctarget, loser_history, health_history, damage_history)
  for i in [0, 1]:
    if healths[i] <= 0:
      bv.yprint("{ctarget} collapses; unit retreats!", templates={"ctarget":actors[i]}, debug=True)
      Event("receive_damage", context.rebase({"damage":actors[i].size,
                                              "ctarget":actors[i],
                                              "dmgdata":"",
                                              "dmglog":""})).activate()

def duel_consider(context, bv, **kwargs):
  csource = context.csource
  ctarget = context.ctarget
  acceptances, duel_data = duel.duel_commit(context, csource, ctarget)
  bv.yprint(str(duel_data), debug=True)
  if acceptances[0]:
    Event.make_speech(csource, context, duel.get_pre_duel_speech("challenge"))
    if acceptances[1]:
      Event.make_speech(ctarget, context, duel.get_pre_duel_speech("accept"))
      Event("duel_accepted", context).activate()
    else:
      Event.make_speech(ctarget, context, duel.get_pre_duel_speech("deny"))

def arrow_strike(context, bv, **kwargs):
  csource = context.csource
  ctarget = context.ctarget
  multiplier = 1
  if "vulnerable" in context.opt and context.vulnerable:
    multiplier = 2
  damage, dmglog = _compute_arrow_damage(csource, ctarget, multiplier=multiplier)
  dmgdata = (csource, ctarget, "shoots", damage)
  Event("receive_damage",
        context.rebase({"damage":damage, "ctarget":ctarget, "dmgdata":dmgdata, "dmglog":dmglog})).activate()
  if csource.has_unit_status("fire_arrow"):
    if random.random() < 0.5 and not context.battle.is_raining():
      bv.disp_skill_narration("fire_arrow", "{}'s arrows are covered with fire!".format(csource), True)
      Event.make_speech(csource, context, "Light'em up!")
      Event.gain_status("burned", context, ctarget)
  if csource.has_unit_status("chu_ko_nu"):
    if random.random() < 0.5:
      bv.disp_skill_narration("chu_ko_nu", "{}'s arrows continue to rain!".format(csource), True)
      if random.random() < 0.5 and csource.name == "Zhuge Liang":
        Event.make_speech(csource, context, "The name is a bit embarassing...")
      else:
        Event.make_speech(csource, context, "Have some more!")
      Event("arrow_strike", context).activate()
  if ctarget.has_unit_status("counter_arrow"):
    if random.random() < 0.85:
#      bv.yprint("  <counter arrow skill> %s can counter with their own volley of arrows" % ctarget)
      Event("counter_arrow_strike", context.rebase_switch()).activate()

def physical_clash(context, bv, **kwargs):
  csource = context.csource
  ctarget = context.ctarget
  bv.yprint("  {} clashes against {}!".format(csource, ctarget))
  Event("physical_strike", context).activate()
  # bv.yprint("  %s able to launch retaliation" % ctarget) can die in the middle
  Event("physical_strike", context.rebase_switch()).activate()
  
def physical_strike(context, bv, **kwargs):
  """ strike is the singular act of hitting """
  csource = context.csource
  ctarget = context.ctarget
  damage, damlog = _compute_physical_damage(csource, ctarget, multiplier=1)
  dmgdata = (csource, ctarget, "hits", damage)
  ctarget.attacked_by.append(csource)
  csource.attacked.append(ctarget)
  Event("receive_damage", context.rebase({"damage":damage,
                                          "ctarget":ctarget,
                                          "dmgdata":dmgdata,
                                          "dmglog":damlog})).activate()

EVENTS_GENERIC_CTARGETTED = {
  "arrow_strike": {},
  "duel_consider": {},
  "duel_accepted": {},
  "engage": {},
  "march": {},
  "indirect_raid": {},
  "physical_clash": {},
  "physical_strike": {}
}

for ev in EVENTS_GENERIC_CTARGETTED:
  EVENTS_GENERIC_CTARGETTED[ev]["panic_blocked"] = True
  EVENTS_GENERIC_CTARGETTED[ev]["actors"] = ["csource", "ctarget"]
  EVENTS_GENERIC_CTARGETTED[ev]["primary_actor"] = "csource"

###############
# MISC EVENTS #
###############

# eventually maybe separate things out with one ctarget unit
  
EVENTS_MISC = {
  # "army_destroyed": {
  #   "actors":["ctarget_army"],
  #   "primary_actor": "ctarget_army"
  # },
  "make_speech": {
    "actors":["ctarget"],
    "primary_actor": "ctarget"
  },
  "receive_damage": {
    "actors":["ctarget"],
    "primary_actor": "ctarget"
  },
  "receive_status": {
    "actors":["ctarget"],
    "primary_actor": "ctarget"
    #"need_live_actors":False # maybe need "Captured" etc.
  },
  "order_change": {
    "actors":["ctarget_army"],
    "primary_actor": "ctarget_army"
  },
  "change_morale": {
    "actors":["ctarget_army"],
    "primary_actor": "ctarget_army"
  },
  "order_yomi_win": {
    "actors":["ctarget_army"],
    "primary_actor": "ctarget_army"
  },
}

# for ev in EVENTS_RECEIVE:
#   EVENTS_RECEIVE[ev]["panic_blocked"] = True
# No common rules here...

def receive_damage(context, bv, **kwargs):
  ctarget = context.ctarget
  damage = context.damage
  dmgdata = context.dmgdata
  if damage >= ctarget.size:
    damage = ctarget.size
  dmglog = context.dmglog or None
  bv.disp_damage(battle_constants.ARMY_SIZE_MAX,
                                          ctarget.size, damage, dmgdata, dmglog)
  ctarget.size -= damage
  if ctarget.size <= 0:
    ctarget.leave_battle()

def receive_status(context, bv, **kwargs):
  ctarget = context.ctarget
  stat_str = context.status
  if "on_receive" in status.STATUSES_BATTLE[stat_str]:
    # sometimes can be quiet
    disp = status.STATUSES_BATTLE[stat_str]["on_receive"].format(**context.opt)
    bv.yprint("  " + disp)
  ctarget.add_unit_status(stat_str)

# for armies

def order_change(context, bv, **kwargs):
  """
  When an order changes, if it happens to lose the Yomi, then the cost of the morale is
  'bet' and will be removed if the opponent out-Yomi's you.
  """
  ctarget_army = context.ctarget_army
  morale_bet = context.morale_bet
  bv.yprint("It was a feint. {ctarget_army} suddenly " +
                        rps.order_info(ctarget_army.get_order(), "verb") + ".",
                        templates={"ctarget_army":ctarget_army})
  ctarget_army.bet_morale_change = morale_bet
  # Event("change_morale", context).activate() this cost is pretty high

def change_morale(context, bv, **kwargs):
  ctarget_army = context.ctarget_army
  morale_change = context.morale_change
  newmorale = ctarget_army.morale + morale_change
  newmorale = min(newmorale, battle_constants.MORALE_MAX)
  newmorale = max(newmorale, battle_constants.MORALE_MIN)
  ctarget_army.morale = newmorale

def order_yomi_win(context, bv, **kwargs):
  csource_army = context.ctarget_army
  ctarget_army = context.battle.armies[1-csource_army.armyid]
  ycount = csource_army.get_yomi_count()
  bet = ctarget_army.bet_morale_change + 1
  Event("change_morale", context.rebase(opt={"ctarget_army":csource_army, # winning army
                                             "morale_change":ycount})).activate()
  Event("change_morale", context.rebase(opt={"ctarget_army":ctarget_army, # losing army
                                             "morale_change":-bet})).activate()
  # must put after to show the difference
  bv.disp_yomi_win(csource_army, ctarget_army, ycount, bet)

################################
# targetted Events from Skills #
################################

def counter_arrow_strike(context, bv, **kwargs):
  csource = context.csource
  ctarget = context.ctarget
  bv.disp_skill_narration("counter_arrow", "{} counters with their own volley".format(csource), True)
  Event.make_speech(csource, context, "Let's show them guys how to actually use arrows!")
  Event("arrow_strike",
        context.rebase({"csource":csource, "ctarget":ctarget})).activate()
  return True

# Tactics

def lure_tactic(context, base_chance, improved_chance, success_callback):
  """
  a bit harder since we dont know who the lurer actually is

  context needs:
    csource
    ctarget
    success_callback
  """
  bv = context.battle.battlescreen
  csource = context.csource
  ctarget = context.ctarget
  base_lure_chance = base_chance
  improved_lure_chance = improved_chance
  additional_activations = []
  possible_aoe = tuple([u for u in context.ctarget.position.units[ctarget.army.armyid] if u != ctarget])
  possible_lure_candidates = tuple(context.battle.armies[csource.army.armyid].present_units())
  # eventually make it just the people who are in position
  lure_candidates = tuple(lc for lc in possible_lure_candidates if lc.has_unit_status("lure_skill"))
    # later: probably also add a check of panicked, etc.
  for targ in possible_aoe:
    roll = random.random()
    if roll > improved_lure_chance:
      continue
    elif roll > base_lure_chance and not lure_candidates: # we do not activate
      continue
    else: # we activate
      if roll > base_lure_chance:
        # this means we came from a lure
        lurer = random.choice(lure_candidates)
        bv.disp_skill_narration("lure_skill", "", True)
        Event.make_speech(lurer, context, skills.get_skill_speech("lure_skill", "on_success_speech")[1])
        lure_success_text = skills.skill_info("lure_skill", "on_success")
        bv.disp_skill_narration("lure_skill", lure_success_text.format(**{"lurer":lurer, "ctarget":targ}), True)
      else:
        # still a success, but it is not because of the lure
        bv.yprint("{ctarget} was also entangled into the tactic!".format(**{"ctarget":targ}))
      additional_activations.append(targ)
  for targ in tuple(additional_activations):
    success_callback(context.rebase({"csource":csource,
                                     "ctarget":targ}))

def target_skill_tactic(context, skillcard, cchance, success_callback):
  """
  For a class of tactics with a source, a target, a skill, and corresponding roll. This event
  happens the moment the conditions activate, so we are rolling for success.

  Context needs:
    csource,
    ctarget,
    success_callback
  """
  bv = context.battle.battlescreen
  success = random.random() < cchance # can replace with harder functions later
  # TODO cchance = calc_chance(target, skill) or something
  skillcard_on_prep = skills.get_skillcard_speech(skillcard, "on_roll").format(**context.opt)
  bv.disp_skill_narration(skillcard, skillcard_on_prep)
  if success:
    narrator_str, narrate_text = skills.get_skillcard_speech(skillcard, "on_success_speech")
    Event.make_speech(context.opt[narrator_str], context, narrate_text)
    success_callback(context)
    lure_tactic(context,
                0.25, # base entanglement chance
                0.6, # improved entanglement chance
                success_callback)
  else:
    narrator_str, narrate_text = skills.get_skillcard_speech(skillcard, "on_fail_speech")
    Event.make_speech(context.opt[narrator_str], context, narrate_text)
  bv.disp_skill_narration(skillcard, "", success)
  return success

def _fire_tactic_success(context):
  Event.gain_status("burned", context, context.ctarget)

def fire_tactic(context, bv, **kwargs):
  return target_skill_tactic(context, "fire_tactic", 0.5, _fire_tactic_success)

def jeer_tactic(context, bv, **kwargs):
  csource = context.csource
  ctarget = context.ctarget
  # should interrupt this, but right now it should be fine
  success = random.random() < 0.3
  bv.disp_skill_narration("jeer_tactic",
                  "{} prepares their best insults...".format(csource))
  ins = random.choice(insults.INSULTS)
  Event.make_speech(csource, context, ins[0])
  if success:
    Event.make_speech(ctarget, context, "Why you...")
    Event.gain_status("provoked", context, ctarget)
    # TODO: AOE
  else:
    Event.make_speech(ctarget, context, ins[1])
  bv.disp_skill_narration("jeer_tactic", "", success)
  return success

def _panic_tactic_success(context):
  Event.gain_status("panicked", context, context.ctarget)

def panic_tactic(context, bv, **kwargs):
  return target_skill_tactic(context, "panic_tactic", 0.5, _panic_tactic_success)

def _flood_tactic_success(context):
  damdice = battle_constants.FLOOD_TACTIC_DAMDICE
  damage = random.choice(range(damdice))
  dmgdata = (context.csource, context.ctarget, "floods", damage)
  Event("receive_damage", context.copy(
    additional_opt={"damage":damage, "dmgdata":dmgdata, "dmglog":""})).activate()
  
def flood_tactic(context, bv, **kwargs):
  return target_skill_tactic(context, "flood_tactic", 0.5, _flood_tactic_success)
  
EVENTS_SKILLS = {
  "counter_arrow_strike": {
    "can_aoe": False
    },
  "fire_tactic": {
    "can_aoe": True
    },
  "jeer_tactic": {
    "can_aoe": True
    },
  "lure_tactic": {
    },
  "panic_tactic": {
    "can_aoe": True
    },
  "flood_tactic": {
    "can_aoe": True
    }
}

for ev in EVENTS_SKILLS:
  EVENTS_SKILLS[ev]["panic_blocked"] = True
  EVENTS_SKILLS[ev]["actors"] = ["csource", "ctarget"]
  EVENTS_SKILLS[ev]["primary_actor"] = "csource"

#######################################
# Status Beginning/end of turn Events #
#######################################

def generic_eot_fizzle(context, bv, **kwargs):
  # a bit annoying that removal is not symmetric with gaining
  stat_str = context.status
  if status.status_info(stat_str, "on_remove"):
    # eventually, maybe do specialized stuff
    bv.yprint("{} is no longer {}".format(context.ctarget, status.Status(stat_str)))
  context.ctarget.remove_unit_status(stat_str)
  
def burned_bot(context, bv, **kwargs):
  ctarget = context.ctarget
  if context.battle.is_raining():
    bv.yprint("thanks to the rain, %s put out the fire." % ctarget)
    ctarget.remove_unit_status("burned")
  
def burned_eot(context, bv, **kwargs):
  ctarget = context.ctarget
  if ctarget.has_unit_status("burned"): # could have dried up or something
    # damage before putting out
    if context.battle.is_hot():
      damdice = 10
      bv.yprint("It's an extra {} day; fire is much more dangerous.".format(context.battle.weather))
    else:
      damdice = 5
    damage = random.choice(range(damdice))
    dmgdata = (None, ctarget, "burned", damage)
    Event("receive_damage", context.copy(
      additional_opt={"damage":damage, "dmgdata":dmgdata, "dmglog":""})).activate()
    if random.random() < 0.5:
      bv.yprint("{} has put out the fire.".format(ctarget))
      ctarget.remove_unit_status("burned")
    else:
      bv.yprint("The fire burning %s rages on." % ctarget)

def berserk_eot(context, bv, **kwargs):
  ctarget = context.ctarget
  if ctarget.has_unit_status("berserk"): # could have dried up or something
    if random.random() < 0.5:
      bv.yprint("%s regains control." % ctarget)
      ctarget.remove_unit_status("berserk")
    else:
      bv.yprint("{}'s unit is still {}.".format(ctarget, status.Status("berserk")))

def panicked_eot(context, bv, **kwargs):
  ctarget = context.ctarget
  if ctarget.has_unit_status("panicked"): # could have dried up or something
    if random.random() < 0.5:
      bv.yprint("%s regains control." % ctarget)
      ctarget.remove_unit_status("panicked")
    else:
      bv.yprint("%s's unit is still panicking." % ctarget)

def provoked_eot(context, bv, **kwargs):
  ctarget = context.ctarget
  if ctarget.has_unit_status("provoked"): # could have dried up or something
    if random.random() < 0.5:
      bv.yprint("%s regains control." % ctarget)
      ctarget.remove_unit_status("provoked")
    else:
      bv.yprint("{}'s unit is still {}.".format(ctarget, status.Status("provoked")))

##########
# Skills #
##########

def trymode_status_bot(context, bv, **kwargs):
  ctarget = context.ctarget
  trymodeprob = (ctarget.size_base-ctarget.size)/ctarget.size_base
  success = random.random() < trymodeprob
  bv.disp_skill_narration("trymode", "{} looks for an excuse to pretend to be powered up...".format(ctarget))
  if success:
    # import pdb; pdb.set_trace()
    Event.make_speech(ctarget, context, "Did you really think I took you seriously before?")
    Event.gain_status("trymode_activated", context, ctarget)
  else:
    Event.make_speech(ctarget, context, "Nope, still not trying.")
  bv.disp_skill_narration("trymode", "", success)

EVENTS_STATUS = {
  "generic_eot_fizzle": {},
  "burned_bot": {},
  "burned_eot": {},
  "berserk_eot": {},
  "provoked_eot": {},
  "panicked_eot": {},
  "trymode_status_bot": {}
}

for ev in EVENTS_STATUS:
  EVENTS_STATUS[ev]["panic_blocked"] = True
  EVENTS_STATUS[ev]["actors"] = ["ctarget"]
  EVENTS_STATUS[ev]["primary_actor"] = "ctarget"

EVENTS = dict(list(EVENTS_ORDERS.items()) +
              list(EVENTS_GENERIC_CTARGETTED.items()) +
              list(EVENTS_MISC.items()) +
              list(EVENTS_SKILLS.items()) +
              list(EVENTS_STATUS.items()))
