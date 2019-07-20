import csv
import random

from utils import str_to_bool
import battle_constants
import contexts
import duel
import rps
import skills
import status
import textutils

# <2019-07-04 Thu>
# had both statuses and skills here, and decided to offload all skills into statuses, and so
# now only have to think about interplays between statuses and events (as opposed to aslo have)
# skills involved

def event_csv_loader(filestr):
  with open(filestr, "r") as csvfile:
    mydict = {}
    reader = csv.reader(csvfile, delimiter=',')
    next(reader)
    for row in reader:
      mydict[row[0]] = {"event_type":row[2].strip(),
                        "actor_type":row[1].strip(),
                        "can_aoe":str_to_bool(row[3].strip()),
                        "panic_blocked":str_to_bool(row[4].strip())}
    return mydict
    
EVENTS = event_csv_loader("events.csv")
ACTORS_DICT = {
  "unit_single":["ctarget"],
  "army_single":["ctarget_army"],
  "unit_double":["csource", "ctarget"],
  "none":[],
}
PRIMARY_ACTOR_DICT = {
  "unit_single":"ctarget",
  "army_single":"ctarget_army",
  "unit_double":"csource",
}

class Event():
  """
  Not true events since I didn't really set up Handlers, etc; really just glorified functions
  with wrapper logic.
  """
  
  def __init__(self, battle, event_name, context):
    self.battle = battle
    self.event_name = event_name
    # this is so we don't have to write it for lots of functions
    self.event_func = globals().get(event_name, None)
    self.context = context

  def get_actor_type(self):
    actor_type = event_info(self.event_name, "actor_type")
    if actor_type is None:
      return "none"  # this is so ACTORS_DICT returns correctly an empty list
    else:
      return actor_type
      
  def activate(self, *args):
    # death handler (should later be "availability" for retreats, etc.)
    # most events require actors who are alive; TODO: exceptions?
    if any([not self.context.opt[foo].is_present() for foo in ACTORS_DICT[self.get_actor_type()]]): #pylint:disable=blacklisted-name
      # TODO: exceptions for things like unit_destroyed or army_destroyed
      return
    # panic handler
    if event_info(self.event_name, "panic_blocked"):
      potential_panicker = getattr(self.context, PRIMARY_ACTOR_DICT[self.get_actor_type()])
      if potential_panicker.has_unit_status("panicked"):
        self.battle.narrator.narrate_status("on_activation",
                                            contexts.Context({'ctarget':potential_panicker,
                                                              'stat_str':'panicked'}))
        return
    # narrator handler
    self.battle.narrator.notify(self, *args)
    # time to activate this event on the queue; note the event has its own context, battle, etc.
    if self.event_func:
      self.event_func(self.battle,
                      self.context,
                      self.battle.battlescreen,
                      self.battle.narrator, *args)

def event_info(event_name, key):
  """ Main auxilary function; gets a piece of info about an event type, and None otherwise."""
  edict = EVENTS.get(event_name, None)
  if edict:
    return edict.get(key, None)

#####################
# Utility functions #
#####################

# Damage functions

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
  raw_damage, hitprob = _roll_dice(s_str, d_str, dicecount)
  dmglog = tuple((s_str, d_str, dicecount, hitprob, raw_damage))
  # we pass this on for MVC purposes
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

def order_received(battle, context, bv, narrator):
  """
  Handles statuses, etc. that affects receiving of an order.
  """
  ctarget = context.ctarget
  given_order = context.order
  if ctarget.has_unit_status("panicked") and random.random() < 0.5:
    Event(battle, "panicked_order", context).activate()
    return
  if ctarget.has_unit_status("provoked") and random.random() < 0.5:
    Event(battle, "provoked_order", context).activate()
    return
  Event(battle, rps.order_to_event(given_order), context).activate()

def attack_order(battle, context, bv, narrator):
  """
  what we do in a *committed* attack order (we no longer consider statuses, etc;)
  """
  ctarget = context.ctarget
  ctarget.order = rps.FinalOrder('A')
  myarmyid = ctarget.army.armyid
  enemy = battle.armies[1-myarmyid]
  enemyunits = enemy.present_units()
  if not enemyunits:
    bv.yprint("No unit to attack!", mode=["huddle"])
    ctarget.targetting = ("defending", ctarget)
    return
  cnewsource = context.ctarget # new event
  cnewtarget = random.choice(enemyunits)
  cnewsource.targetting = ("marching", cnewtarget)
  bv.yprint("{}: marching -> {};".format(cnewsource, cnewtarget), mode=["huddle"])
  newcontext = contexts.Context({"csource":cnewsource, "ctarget":cnewtarget})
  battle.place_event("march", newcontext, "Q_MANUEVER")

def defense_order(battle, context, bv, narrator):
  ctarget = context.ctarget
  ctarget.order = rps.FinalOrder('D')
  ctarget.targetting = ("defending", ctarget)
  ctarget.move(battle.hqs[ctarget.army.armyid])
  bv.yprint("{}: staying put at {};".format(ctarget, context.ctarget.position), mode=["huddle"])
  Event(battle, "gain_status", context).activate("defended")

def indirect_order(battle, context, bv, narrator):
  ctarget = context.ctarget
  ctarget.order = rps.FinalOrder('I')
  myarmyid = ctarget.army.armyid
  enemy = battle.armies[1-myarmyid]
  enemyunits = enemy.present_units()
  if not enemyunits:
    bv.yprint("No unit to target!", mode=["huddle"])
    ctarget.targetting = ("defending", ctarget)
    return
  cnewsource = ctarget  # new event
  cnewtarget = random.choice(enemyunits)
  cnewsource.targetting = ("sneaking", cnewtarget)
  bv.yprint("{}: sneaking -> {}; planning skullduggery".format(cnewsource, cnewtarget), mode=["huddle"])
  newcontext = contexts.Context({"csource":cnewsource, "ctarget":cnewtarget})
  battle.place_event("indirect_raid", newcontext, "Q_MANUEVER")

def panicked_order(battle, context, bv, narrator):
  #  could just call this order, though this way the narrator picks up this situation
  defense_order(battle, context, bv, narrator)

def provoked_order(battle, context, bv, narrator):
  attack_order(battle, context, bv, narrator)

############################################
# Meta events about the orders themeselves #
############################################

def order_change(battle, context, bv, narrator):
  """
  When an order changes, if it happens to lose the Yomi, then the cost of the morale is
  'bet' and will be removed if the opponent out-Yomi's you.
  """
  ctarget_army = context.ctarget_army
  morale_bet = context.morale_bet
  ctarget_army.bet_morale_change = morale_bet

def order_yomi_win(battle, context, bv, narrator):
  csource_army = context.ctarget_army
  ctarget_army = battle.armies[1-csource_army.armyid]
  ycount = csource_army.get_yomi_count()
  bet_bool = bool(ctarget_army.bet_morale_change > 0)
  morale_dam = ctarget_army.bet_morale_change + ycount 
  Event(battle, "change_morale", contexts.Context({"ctarget_army":csource_army, # winning army
                                             "morale_change":ycount})).activate()
  # definitely need this
  Event(battle, "change_morale", contexts.Context({"ctarget_army":ctarget_army, # losing army
                                             "morale_change":-morale_dam})).activate()
  # must put after to show the difference
  bv.disp_yomi_win(csource_army, ctarget_army, ycount, morale_dam, bet_bool)

##################
# Manuever Phase #
##################

# The units move around, retarget, etc; no damage is actually done; all these things are put
# on the main queue, Q_RESOLVE

def march(battle, context, bv, narrator):
  csource = context.csource
  ctarget = context.ctarget
  # if ctarget in csource.attacked_by:
  if csource.attacked_by:
    # currently, this never activates since the order phase doesn't change attacked_by...
    Event(battle, "action_already_used", context).activate()
    return
  ctarget.attacked_by.append(csource)
  csource.attacked.append(ctarget)
  if ctarget.is_defended():
    Event(battle, "engage", context.clean_switch()).activate()
  else:
    Event(battle, "engage", context).activate()
  converging = bool(ctarget.targetting[1] == csource) # if other ctarget is coming towards you
  if ctarget.is_defended():
    assert ctarget.position == battle.hqs[ctarget.army.armyid] # meeting at hq
    csource.move(ctarget.position)
    bv.yprint("  %s able to launch defensive arrow volley" % ctarget, debug=True)
    battle.place_event("arrow_strike", context.clean_switch(), "Q_RESOLVE")
    if random.random() < 0.5:
      bv.yprint("  %s able to launch offensive arrow volley" % csource, debug=True)
      battle.place_event("arrow_strike", context, "Q_RESOLVE")
    battle.place_event("physical_clash", context.clean_switch(), "Q_RESOLVE")
  else:
    newpos = battle.make_position(ctarget)
    csource.move(newpos)
    ctarget.move(newpos)
    if random.random() < 0.5:
      bv.yprint("  %s able to launch offensive arrow volley" % csource, debug=True)
      battle.place_event("arrow_strike", context, "Q_RESOLVE")
    # defense doesn't have time to shoot arrows, unless they were coming in this direction
    if converging:
      if random.random() < 0.5:
        bv.yprint("  %s able to launch defensive arrow volley" % ctarget, debug=True)
        battle.place_event("arrow_strike", context.clean_switch(), "Q_RESOLVE")
    # need logic for when 2 attackers rush into each other
    battle.place_event("physical_clash", context, "Q_RESOLVE")

def indirect_raid(battle, context, bv, narrator):
  csource = context.csource
  ctarget = context.ctarget
  if csource.attacked_by:
    Event(battle, "action_already_used", context).activate()
    return
  Event(battle, "engage", context).activate()
  # tactic 1: raid
  vulnerable = False
  if ctarget.targetting[0] == "defending": # TODO: replace by order check?
    bv.yprint("  {} is caught unawares by the indirect approach!".format(ctarget), debug=True)
    vulnerable = True
  elif ctarget.targetting[0] == "marching":
    bv.yprint("  {}'s marching soldiers are vigilant!".format(ctarget), debug=True)
  battle.place_event("arrow_strike",
                             context.copy({"vulnerable":vulnerable}),
                             "Q_RESOLVE")

def engage(battle, context, bv, narrator):
  """
  What happens when they meet face to face, but before the attacks. All the resolved tactics
  fire off. Tactics only fire when 
  1) they match the order of the unit
  2) they have yomi advantage.
  """
  csource = context.csource
  ctarget = context.ctarget
  army = csource.army
  for sc in army.tableau.bulbed_by(csource):
    if sc.order == csource.order and battle.yomi_winner_id == army.armyid:
      # import pdb; pdb.set_trace()
      newcontext = context.copy({'skillcard':sc})
      battle.place_event(sc.sc_str, newcontext, "Q_RESOLVE")
  if random.random() < battle_constants.DUEL_BASE_CHANCE:
    acceptance, duel_data = duel.duel_commit(context, csource, ctarget)
    if acceptance:
      battle.place_event("duel_challenged", context, "Q_RESOLVE")

#################
# Resolve Phase #
#################

def duel_accepted(battle, context, bv, narrator):
  duelists = [context.csource, context.ctarget]
  ourduel = duel.Duel(context, bv, narrator, duelists)
  # the Duel also gets the renderer and thus 
  healths = ourduel.resolve()
  for i in [0, 1]:
    if healths[i] <= 0:
      bv.yprint("{ctarget} collapses; unit retreats!", templates={"ctarget":duelists[i]}, debug=True)
      Event(battle, "receive_damage", contexts.Context({"damage":duelists[i].size,
                                                        "ctarget":duelists[i],
                                                        "dmgtype":"lost_duel",
                                                        "dmgdata":"",
                                                        "dmglog":""})).activate()
  # it's not always true there is a winner
  has_winner = False
  if healths[0] > 0 and healths[1] <= 0:
    has_winner = True
    winner = context.csource
    loser = context.ctarget
  elif healths[0] <= 0 and healths[1] > 0:
    has_winner = True
    winner = context.ctarget
    loser = context.csource
  newcontext = {"csource":winner, "ctarget":loser}
  if has_winner:
    Event(battle, "duel_defeated", newcontext).activate()

def duel_challenged(battle, context, bv, narrator):
  """
  source already committed, so target sees if he/she is interested
  """
  csource = context.csource
  ctarget = context.ctarget
  acceptance, duel_data = duel.duel_commit(context, ctarget, csource)
  # newcontext = context.copy({'acceptances':acceptances})
  if acceptance:
    Event(battle, "duel_accepted", context).activate()
  else:
    Event(battle, "duel_rejected", context).activate()
      
def arrow_strike(battle, context, bv, narrator):
  csource = context.csource
  ctarget = context.ctarget
  multiplier = 1
  wording = "shoots"
  if "vulnerable" in context.opt and context.vulnerable:
    multiplier = 2
    wording = "heavily shoots"
  damage, dmglog = _compute_arrow_damage(csource, ctarget, multiplier=multiplier)
  dmgdata = (csource, ctarget, wording, damage)
  Event(battle, "receive_damage", contexts.Context({"damage":damage,
                                                    "ctarget":ctarget,
                                                    "dmgtype":"arrow",
                                                    "dmgdata":dmgdata,
                                                    "dmglog":dmglog})).activate()
  if csource.has_unit_status("fire_arrow"): 
    Event(battle, 'fire_arrow', context).activate()
  if csource.has_unit_status("chu_ko_nu"):
    Event(battle, 'chu_ko_nu', context).activate()
  elif ctarget.has_unit_status("counter_arrow"):
    Event(battle, 'counter_arrow', context).activate()

def physical_clash(battle, context, bv, narrator):
  csource = context.csource
  ctarget = context.ctarget
  vulnerable = (csource.order == rps.FinalOrder('A')) and (ctarget.order == rps.FinalOrder('I'))
  Event(battle, "physical_strike", context.copy({"vulnerable":vulnerable})).activate()
  # bv.yprint("  %s able to launch retaliation" % ctarget) can die in the middle
  if random.random() < 0.5:
    Event(battle, "physical_strike", context.clean_switch()).activate()
  
def physical_strike(battle, context, bv, narrator):
  """ strike is the singular act of hitting """
  csource = context.csource
  ctarget = context.ctarget 
  multiplier = 1
  wording = "hits"
  if "vulnerable" in context.opt and context.vulnerable:
    multiplier = 2
    wording = "heavily hits"
  damage, damlog = _compute_physical_damage(csource, ctarget, multiplier=multiplier)
  dmgdata = (csource, ctarget, wording, damage)
  Event(battle, "receive_damage", contexts.Context({"damage":damage,
                                          "ctarget":ctarget,
                                          "dmgdata":dmgdata,
                                          "dmglog":damlog})).activate()


###############
# MISC EVENTS #
###############

# for ev in EVENTS_RECEIVE:
#   EVENTS_RECEIVE[ev]["panic_blocked"] = True
# No common rules here...

def receive_damage(battle, context, bv, narrator):
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
    Event(battle, "unit_leave_battle", context).activate()

def unit_leave_battle(battle, context, bv, narrator):
  ctarget = context.ctarget
  army = ctarget.army
  if random.random() < 0.5:  # capture chance
    state = 'CAPTURED'
    Event(battle, "unit_captured", context).activate()
  else:
    state = 'ESCAPED'
    Event(battle, "unit_escaped", context).activate()
  ctarget.leave_battle(state) 
  if not army.is_present():
    Event(battle, "army_leave_battle", context={'ctarget_army':army}).activate()
  else:
    # compute morale change from leaving battle
    if ctarget.is_commander:
      damage = army.morale
    else:
      damage = 2
    Event(battle, "change_morale", contexts.Context({"ctarget_army":army,
                                                     "morale_change":-damage})).activate()
    Event(battle, "change_morale", contexts.Context({"ctarget_army":battle.armies[1-army.armyid],
                                                     "morale_change":damage})).activate()

def change_morale(battle, context, bv, narrator):
  ctarget_army = context.ctarget_army
  if ctarget_army.morale <= 0:
    return
  morale_change = context.morale_change
  newmorale = ctarget_army.morale + morale_change
  newmorale = min(newmorale, battle_constants.MORALE_MAX)
  newmorale = max(newmorale, battle_constants.MORALE_MIN)
  ctarget_army.morale = newmorale
  if ctarget_army.morale <= 0:
    Event(battle, "army_collapse_from_morale", context).activate()
    for u in tuple(ctarget_army.present_units()):
      Event(battle, "unit_leave_battle", contexts.Context({'ctarget':u})).activate()

################################
# targetted Events from Skills #
################################

def _resolve_entanglement(battle, context, bv, narrator):
  """
  a bit harder since we dont know who the lurer actually is

  context needs:
    csource
    ctarget
    success_callback
  """
  csource = context.csource
  ctarget = context.ctarget
  base_entanglement_chance = 0.1
  additional_activations = []
  possible_aoe = tuple([u for u in context.ctarget.position.units[ctarget.army.armyid] if u != ctarget])
  # eventually make it just the people who are in position
  lure_candidates = tuple(lc for lc in
                           tuple(battle.armies[csource.army.armyid].present_units())
                           if lc.has_unit_status("lure_skill"))
    # later: probably also add a check of panicked, etc.
  for new_target in possible_aoe:
    roll = random.random()
    if roll < base_entanglement_chance:
      # still a success, but it is not because of the lure
      bv.yprint("{ctarget} was also entangled into the tactic!".format(**{"ctarget":new_target}))
      additional_activations.append(new_target)
    elif lure_candidates: # lure roll is available
      # make a lure roll
      lurer = random.choice(lure_candidates)
      successes = _roll_target_skill_tactic(battle,
                                            context.copy({"lurer":lurer,
                                                          "ctarget":new_target}), bv,
                                            narrator, "lure_tactic", 0.20)
      # TODO: add chain tactic for Pang Tong
      # either has 1 or 0 elements
      if successes:
        assert len(successes) == 1
        bv.yprint("{ctarget} was also entangled into the tactic!".format(**{"ctarget":new_target}))
        additional_activations.append(successes[0])
  return additional_activations

def _roll_target_skill_tactic(battle, context, bv, narrator, roll_key, cchance):
  """
  We are about to roll something for success.

  Context needs:
    csource,
    ctarget,
    success_callback

  returns:
    a list of successful targets (could be several due to entanglement, lures, etc.)
  """
  commitment_guarantee = False
  if (event_info(roll_key, 'event_type') == 'target-skill' and
      roll_key in skills.SKILLCARDS.keys() and  # hack to not include things like lure
      context.csource.army.commitment_bonus):
    commitment_guarantee = True
    new_chance = 1.1
  else:
    new_chance = cchance
  success = random.random() < new_chance # can replace with harder functions later
  Event(battle, "roll_success", context).activate(roll_key, success, commitment_guarantee)
  successful_targets = []
  if success:
    successful_targets.append(context.ctarget)
    if event_info(roll_key, "can_aoe"):
      successful_targets += _resolve_entanglement(battle, context, bv, narrator)
  Event(battle, "roll_post_success", context).activate(roll_key, success)
  return successful_targets

def resolve_targetting_event(battle, context, bv, narrator, roll_key, cchance, success_func):
  successful_targets = _roll_target_skill_tactic(battle, context, bv, narrator, roll_key, cchance)
  results = []
  for new_target in successful_targets:
    new_context = context.copy({"ctarget":new_target})
    # todo: can eventually get new kwords this way
    results.append((new_target, success_func(battle, new_context)))
  return results
                          
##########################################
# Targetting from skills -- no skillcard #
##########################################

def _fire_arrow_success(battle, context): # eventually these should not be events...
  Event(battle, "gain_status", context).activate("burned")

def fire_arrow(battle, context, bv, narrator):
  if not battle.is_raining():
    chance = 0.5
  else:
    chance = -0.1
  results = resolve_targetting_event(battle, context, bv, narrator, "fire_arrow", chance, _fire_arrow_success)

def _chu_ko_nu_success(battle, context): 
  Event(battle, 'arrow_strike', context).activate()

def chu_ko_nu(battle, context, bv, narrator):
  chance = 0.5
  results = resolve_targetting_event(battle, context, bv, narrator, "chu_ko_nu", chance, _chu_ko_nu_success)

def _counter_arrow_success(battle, context): 
  Event(battle, "arrow_strike", context).activate()  # this is already switched
  
def counter_arrow(battle, context, bv, narrator):
  chance = 0.8
  newcontext = context.clean_switch() #  kill things like "vulnerable"
  results = resolve_targetting_event(battle, newcontext, bv, narrator, "counter_arrow", chance, _counter_arrow_success)

##############
# Skillcards #
##############

def _fire_tactic_success(battle, context): # eventually these should not be events...
  Event(battle, "gain_status", context).activate("burned")

def fire_tactic(battle, context, bv, narrator):
  chance = 0.5
  context.skillcard.make_visible_to_all()
  results = resolve_targetting_event(battle, context, bv, narrator, "fire_tactic", chance, _fire_tactic_success)

def _jeer_tactic_success(battle, context):
  Event(battle, "gain_status", context).activate("provoked")
  
def jeer_tactic(battle, context, bv, narrator):
  chance = 0.5
  context.skillcard.make_visible_to_all()
  results = resolve_targetting_event(battle, context, bv, narrator, "jeer_tactic", chance, _jeer_tactic_success)

def _panic_tactic_success(battle, context):
  Event(battle, "gain_status", context).activate("panicked")

def panic_tactic(battle, context, bv, narrator):
  chance = 0.5
  context.skillcard.make_visible_to_all()
  results = resolve_targetting_event(battle, context, bv, narrator, "panic_tactic", chance, _panic_tactic_success)

def _flood_tactic_success(battle, context):
  damdice = battle_constants.FLOOD_TACTIC_DAMDICE
  damage = random.choice(range(damdice))
  dmgdata = (context.csource, context.ctarget, "floods", damage)
  Event(battle, "receive_damage", context.copy(
    {"damage":damage, "dmgdata":dmgdata, "dmglog":""})).activate()

def flood_tactic(battle, context, bv, narrator):
  chance = 0.5
  context.skillcard.make_visible_to_all()
  results = resolve_targetting_event(battle, context, bv, narrator, "flood_tactic", chance, _flood_tactic_success)
                          
##########
# Status #
##########

def gain_status(battle, context, bv, narrator, stat_str):
  """
  nothing should call add_unit_status except for this, so all the handlers are there.
  
  This will call gain_status_event with the right context put in
  """
  ctarget = context.ctarget
  ctarget.add_unit_status(stat_str)
  narrator.narrate_status("on_receive", context.copy(
    {"stat_str":stat_str, "stat_viz":status.Status(stat_str).stat_viz()}))

def remove_status_probabilistic(battle, context, bv, narrator):
  """ 
  context:
    status
    fizzle_prob
  """
  # a bit annoying that removal is not symmetric with gaining
  ctarget = context.ctarget
  stat_str = context.stat_str
  assert ctarget.has_unit_status(stat_str)
  fizzle_prob = context.fizzle_prob
  if (random.random() < fizzle_prob):
    context.ctarget.remove_unit_status(stat_str)
    narrator.narrate_status("on_remove", context)
  else:
    narrator.narrate_status("on_retain", context)

def burned_bot(battle, context, bv, narrator):
  ctarget = context.ctarget
  if battle.is_raining():
    bv.yprint("thanks to the rain, %s put out the fire." % ctarget)
    ctarget.remove_unit_status("burned")
    
def burned_eot(battle, context, bv, narrator):
  ctarget = context.ctarget
  if ctarget.has_unit_status("burned"): # could have dried up or something
    # damage before putting out
    if battle.is_hot():
      damdice = 10
      bv.yprint("It's an extra {} day; fire is much more dangerous.".format(battle.weather))
    else:
      damdice = 5
    damage = random.choice(range(damdice))
    dmgdata = (None, ctarget, "burned", damage)
    Event(battle, "receive_damage", context.copy(
      {"damage":damage, "dmgdata":dmgdata, "dmglog":""})).activate()
    Event(battle, "remove_status_probabilistic", context.copy({"fizzle_prob": 0.5})).activate()

##########
# Skills #
##########

def _trymode_activation_success(battle, context):
  Event(battle, "gain_status", context).activate("trymode_activated")

def trymode_status_bot(battle, context, bv, narrator):
  ctarget = context.ctarget
  trymodeprob = (ctarget.size_base-ctarget.size)/ctarget.size_base
  resolve_targetting_event(battle, context, bv, narrator, "trymode_status_bot", trymodeprob,
                           _trymode_activation_success)

