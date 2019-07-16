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
}
PRIMARY_ACTOR_DICT = {
  "unit_single":"ctarget",
  "army_single":"ctarget_army",
  "unit_double":"csource",
}

class Event():

  def __init__(self, event_name, context):
    self.event_name = event_name
    self.actor_type = EVENTS[event_name]["actor_type"]
    self.event_func = globals()[event_name]
    self.context = context

  def activate(self):
    edict = EVENTS[self.event_name]
    # death handler (should later be "availability" for retreats, etc.)
    # most events require actors who are alive; TODO: exceptions?
    if any([not self.context.opt[foo].is_present() for foo in ACTORS_DICT[self.actor_type]]): #pylint:disable=blacklisted-name
      # TODO: exceptions for things like unit_destroyed or army_destroyed
      return
    # panic handler
    if event_info(self.event_name, "panic_blocked"):
      potential_panicker = getattr(self.context, PRIMARY_ACTOR_DICT[self.actor_type])
      if potential_panicker.has_unit_status("panicked"):
        self.context.battle.battlescreen.yprint("  %s is %s! No action" % (potential_panicker, status.Status("panicked")))
        return
    # time to activate this event on the queue; note the event has its own context, battle, etc.
    results = self.event_func(self.context,
                              self.context.battle.battlescreen,
                              self.context.battle.narrator)

  @classmethod
  def gain_status(cls, stat_str, context, ctarget):
    """
    Basically, nothing should call add_unit_status except for this, so all the handlers are there.
    """
    Event("receive_status", context=context.rebase({"ctarget":ctarget,
                                                    "stat_str":stat_str,
                                                    "stat_viz":str(status.Status(stat_str))})).activate()

  # @classmethod
  # def event_from_order(cls, battle, unit, order):
  #   """
  #   battle module uses this to get an event based on the intelligence's order
  #   """
  #   return Event("order_received", context=contexts.Context(battle, opt={"ctarget":unit,
  #                                                                      "order":order}))
  
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

def run_event_func(event_name, context, battlescreen, narrator):
  """
  runs one of the event functions in this section by name, giving a context 
  and a view (battlescreen)
  """
  return globals()[event_name](context, battlescreen, narrator)

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

def order_received(context, bv, narrator):
  """
  Handles statuses, etc. that affects receiving of an order.
  """
  ctarget = context.ctarget
  given_order = context.order
  if ctarget.has_unit_status("panicked") and random.random() < 0.5:
    Event("panicked_order", context).activate()
    return
  if ctarget.has_unit_status("provoked") and random.random() < 0.5:
    Event("provoked_order", context).activate()
    return
  Event(rps.order_to_event(given_order), context).activate()

def attack_order(context, bv, narrator):
  """
  what we do in a *committed* attack order (we no longer consider statuses, etc;)
  """
  ctarget = context.ctarget
  ctarget.order = rps.FinalOrder('I')
  myarmyid = ctarget.army.armyid
  enemy = context.battle.armies[1-myarmyid]
  enemyunits = enemy.present_units()
  if not enemyunits: 
    bv.yprint("No unit to attack!")
    ctarget.targetting = ("defending", ctarget)
    return
  cnewsource = context.ctarget # new event
  cnewtarget = random.choice(enemyunits)
  cnewsource.targetting = ("marching", cnewtarget)
  bv.yprint("{}: marching -> {};".format(cnewsource, cnewtarget), debug=True)
  newcontext = context.rebase({"csource":cnewsource, "ctarget":cnewtarget})
  context.battle.place_event("march", newcontext, "Q_MANUEVER")

def defense_order(context, bv, narrator):
  ctarget = context.ctarget
  ctarget.order = rps.FinalOrder('D')
  ctarget.targetting = ("defending", ctarget)
  ctarget.move(context.battle.hqs[ctarget.army.armyid])
  bv.yprint("{}: staying put at {};".format(ctarget, context.ctarget.position), debug=True)
  Event.gain_status("defended", context, ctarget)
  
def indirect_order(context, bv, narrator):
  ctarget = context.ctarget
  ctarget.order = rps.FinalOrder('I')
  myarmyid = ctarget.army.armyid
  enemy = context.battle.armies[1-myarmyid]
  enemyunits = enemy.present_units()
  if not enemyunits:
    bv.yprint("No unit to target!")
    ctarget.targetting = ("defending", ctarget)
    return
  cnewsource = ctarget  # new event
  cnewtarget = random.choice(enemyunits)
  cnewsource.targetting = ("sneaking", cnewtarget)
  bv.yprint("{}: sneaking -> {}; planning strategery".format(cnewsource, cnewtarget), debug=True)
  newcontext = context.rebase({"csource":cnewsource, "ctarget":cnewtarget})
  context.battle.place_event("indirect_raid", newcontext, "Q_MANUEVER")

def panicked_order(context, bv, narrator):
  newcontext = context.copy(additional_opt={"stat_str":"panicked"})
  narrator.narrate_status("on_order_override", **newcontext.opt)
  defense_order(context, bv, narrator)

def provoked_order(context, bv, narrator):
  newcontext = context.copy(additional_opt={"stat_str":"provoked"})
  narrator.narrate_status("on_order_override", **newcontext.opt)
  attack_order(context, bv, narrator)

############################################
# Meta events about the orders themeselves #
############################################

def order_change(context, bv, narrator):
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
  
def order_yomi_win(context, bv, narrator):
  csource_army = context.ctarget_army
  ctarget_army = context.battle.armies[1-csource_army.armyid]
  ycount = csource_army.get_yomi_count()
  bet = ctarget_army.bet_morale_change + ycount 
  Event("change_morale", context.rebase(opt={"ctarget_army":csource_army, # winning army
                                             "morale_change":ycount})).activate()
  Event("change_morale", context.rebase(opt={"ctarget_army":ctarget_army, # losing army
                                             "morale_change":-bet})).activate()
  # must put after to show the difference
  bv.disp_yomi_win(csource_army, ctarget_army, ycount, bet)

  
##################
# Manuever Phase #
##################

# The units move around, retarget, etc; no damage is actually done; all these things are put
# on the main queue, Q_RESOLVE

def march(context, bv, narrator):
  csource = context.csource
  ctarget = context.ctarget
  if ctarget in csource.attacked_by:
    bv.yprint("{} already engaged {}, but they already engaged".format(csource, ctarget), debug=True)
    return
  if ctarget.is_defended():
    readytext = "$[2]$defended!$[7]$"
  else:
    readytext = textutils.disp_unit_targetting(ctarget)
  bv.yprint("{} ({}) marches into {} ({})".format(csource,
                                                      textutils.disp_unit_targetting(csource),
                                                      ctarget,
                                                      readytext), debug=True)
  if ctarget.is_defended():
    Event("engage", context.rebase_switch()).activate()
  else:
    Event("engage", context).activate()
  
  converging = bool(ctarget.targetting[1] == csource) # if other ctarget is coming towards you
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

def indirect_raid(context, bv, narrator):
  csource = context.csource
  ctarget = context.ctarget
  if csource.attacked_by:
    bv.yprint("{}'s sneaking up on {} was interrupted by {}!".format(csource, ctarget, csource.attacked_by[0]))
    return
  bv.yprint("{} ({}) sneaks up on {} ({})".format(csource,
                                                         textutils.disp_unit_targetting(csource),
                                                         ctarget,
                                                         textutils.disp_unit_targetting(ctarget)), debug=True)
  Event("engage", context).activate()
  # tactic 1: raid
  vulnerable = False
  if ctarget.targetting[0] == "defending":
    bv.yprint("  {} is caught unawares by the indirect approach!".format(ctarget), debug=True)
    vulnerable = True
  elif ctarget.targetting[0] == "marching":
    bv.yprint("  {}'s marching soldiers are vigilant!".format(ctarget), debug=True)
  context.battle.place_event("arrow_strike",
                             context.copy(additional_opt={"vulnerable":vulnerable}),
                             "Q_RESOLVE")

def engage(context, bv, narrator):
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
    if sc.order == csource.order and context.battle.yomi_winner == army.armyid:
      context.battle.place_event(sc.sc_str, context, "Q_RESOLVE")
  context.battle.place_event("duel_consider", context, "Q_RESOLVE")

#################
# Resolve Phase #
#################

def duel_accepted(context, bv, narrator):
  duelists = [context.csource, context.ctarget]
  ourduel = duel.Duel(context, bv, narrator, duelists)
  # the Duel also gets the renderer and thus 
  healths = ourduel.resolve()
  for i in [0, 1]:
    if healths[i] <= 0:
      bv.yprint("{ctarget} collapses; unit retreats!", templates={"ctarget":duelists[i]}, debug=True)
      Event("receive_damage", context.rebase({"damage":duelists[i].size,
                                              "ctarget":duelists[i],
                                              "dmgdata":"",
                                              "dmglog":""})).activate()

def duel_consider(context, bv, narrator):
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

def arrow_strike(context, bv, narrator):
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
      bv.disp_activated_narration("fire_arrow", "{}'s arrows are covered with fire!".format(csource), True)
      Event.make_speech(csource, context, "Light'em up!")
      Event.gain_status("burned", context, ctarget)
  if csource.has_unit_status("chu_ko_nu"):
    if random.random() < 0.5:
      bv.disp_activated_narration("chu_ko_nu", "{}'s arrows continue to rain!".format(csource), True)
      if random.random() < 0.5 and csource.name == "Zhuge Liang":
        Event.make_speech(csource, context, "The name is a bit embarassing...")
      else:
        Event.make_speech(csource, context, "Have some more!")
      Event("arrow_strike", context).activate()
  if ctarget.has_unit_status("counter_arrow"):
    if random.random() < 0.85:
#      bv.yprint("  <counter arrow skill> %s can counter with their own volley of arrows" % ctarget)
      Event("counter_arrow_strike", context.rebase_switch()).activate()

def physical_clash(context, bv, narrator):
  csource = context.csource
  ctarget = context.ctarget
  bv.yprint("  {csource} clashes against {ctarget}!", templates=context.opt)
  Event("physical_strike", context).activate()
  # bv.yprint("  %s able to launch retaliation" % ctarget) can die in the middle
  Event("physical_strike", context.rebase_switch()).activate()
  
def physical_strike(context, bv, narrator):
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


###############
# MISC EVENTS #
###############

# for ev in EVENTS_RECEIVE:
#   EVENTS_RECEIVE[ev]["panic_blocked"] = True
# No common rules here...

def receive_damage(context, bv, narrator):
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
    ctarget.leave_battle() # TODO: eventually make into an event
    army = ctarget.army
    if ctarget.is_commander:
      damage = army.morale
    else:
      damage = 2
    Event("change_morale", context.rebase({"ctarget_army":army,
                                           "morale_change":-damage})).activate()
    Event("change_morale", context.rebase({"ctarget_army":context.battle.armies[1-army.armyid],
                                           "morale_change":damage})).activate()

def receive_status(context, bv, narrator):
  ctarget = context.ctarget
  stat_str = context.stat_str
  ctarget.add_unit_status(stat_str)
  narrator.narrate_status("on_receive", **context.opt)

def change_morale(context, bv, narrator):
  ctarget_army = context.ctarget_army
  morale_change = context.morale_change
  newmorale = ctarget_army.morale + morale_change
  newmorale = min(newmorale, battle_constants.MORALE_MAX)
  newmorale = max(newmorale, battle_constants.MORALE_MIN)
  ctarget_army.morale = newmorale


################################
# targetted Events from Skills #
################################

def counter_arrow_strike(context, bv, narrator):
  csource = context.csource
  ctarget = context.ctarget
  bv.disp_activated_narration("counter_arrow", "{} counters with their own volley".format(csource), True)
  Event.make_speech(csource, context, "Let's show them guys how to actually use arrows!")
  Event("arrow_strike",
        context.rebase({"csource":csource, "ctarget":ctarget})).activate()
  return True

# Tactics

def _resolve_entanglement(context, bv, narrator):
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
  base_entanglement_chance = 0.2
  additional_activations = []
  possible_aoe = tuple([u for u in context.ctarget.position.units[ctarget.army.armyid] if u != ctarget])
  # eventually make it just the people who are in position
  lure_candidates = tuple(lc for lc in
                           tuple(context.battle.armies[csource.army.armyid].present_units())
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
      successes = _roll_target_skill_tactic(context.copy(additional_opt={"lurer":lurer,
                                                                      "ctarget":new_target}), bv,
                                            narrator, "lure_tactic", 0.25)
      # TODO: add chain tactic for Pang Tong
      # either has 1 or 0 elements
      if successes:
        assert len(successes) == 1
        bv.yprint("{ctarget} was also entangled into the tactic!".format(**{"ctarget":new_target}))
        additional_activations.append(successes[0])
  return additional_activations

def _roll_target_skill_tactic(context, bv, narrator, roll_key, cchance):
  """
  We are about to roll something for success.

  Context needs:
    csource,
    ctarget,
    success_callback

  returns:
    a list of successful targets (could be several due to entanglement, lures, etc.)
  """
  if (event_info(roll_key, 'event_type') == 'target-skill' and
      roll_key in skills.SKILLCARDS.keys() and  # hack to not include things like lure
      context.csource.army.commitment_bonus):
    narrator.narrate_commitment_guarantee(roll_key, **context.opt)
    new_chance = 1.1
  else:
    new_chance = cchance
  success = random.random() < new_chance # can replace with harder functions later
  # TODO cchance = calc_chance(target, skill) or something
  narrator.narrate_roll(roll_key, success, **context.opt)
  successful_targets = []
  if success:
    successful_targets.append(context.ctarget)
    if event_info(roll_key, "can_aoe"):
      successful_targets += _resolve_entanglement(context, bv, narrator)
  narrator.narrate_roll_post_success(roll_key, success, **context.opt)
  return successful_targets

def resolve_targetting_event(context, bv, narrator, roll_key, cchance, success_func):
  successful_targets = _roll_target_skill_tactic(context, bv, narrator, roll_key, cchance)
  results = []
  for new_target in successful_targets:
    new_context = context.copy(additional_opt={"ctarget":new_target})
    # todo: can eventually get new kwords this way
    results.append((new_target, success_func(new_context)))
  return results

def _fire_tactic_success(context): # eventually these should not be events...
  Event.gain_status("burned", context, context.ctarget)  

def fire_tactic(context, bv, narrator):
  chance = 0.5
  results = resolve_targetting_event(context, bv, narrator, "fire_tactic", chance, _fire_tactic_success)

def _jeer_tactic_success(context):
  Event.gain_status("provoked", context, context.ctarget)
  
def jeer_tactic(context, bv, narrator):
  chance = 0.5
  results = resolve_targetting_event(context, bv, narrator, "jeer_tactic", chance, _jeer_tactic_success)

def _panic_tactic_success(context):
  Event.gain_status("panicked", context, context.ctarget)
  
def panic_tactic(context, bv, narrator):
  chance = 0.5
  results = resolve_targetting_event(context, bv, narrator, "panic_tactic", chance, _panic_tactic_success)

def _flood_tactic_success(context):
  damdice = battle_constants.FLOOD_TACTIC_DAMDICE
  damage = random.choice(range(damdice))
  dmgdata = (context.csource, context.ctarget, "floods", damage)
  Event("receive_damage", context.copy(
    additional_opt={"damage":damage, "dmgdata":dmgdata, "dmglog":""})).activate()

def flood_tactic(context, bv, narrator):
  chance = 0.5
  results = resolve_targetting_event(context, bv, narrator, "flood_tactic", chance, _flood_tactic_success)

#######################################
# Status Beginning/end of turn Events #
#######################################

def remove_status_probabilistic(context, bv, narrator):
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
    narrator.narrate_status("on_remove", **context.opt)
  else:
    narrator.narrate_status("on_retain", **context.opt)
  
def burned_bot(context, bv, narrator):
  ctarget = context.ctarget
  if context.battle.is_raining():
    bv.yprint("thanks to the rain, %s put out the fire." % ctarget)
    ctarget.remove_unit_status("burned")
    
def burned_eot(context, bv, narrator):
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
    Event("remove_status_probabilistic", context.copy(additional_opt={
      "fizzle_prob": 0.5})).activate()

##########
# Skills #
##########

def _trymode_activation_success(context):
  Event.gain_status("trymode_activated", context, context.ctarget)

def trymode_status_bot(context, bv, narrator):
  ctarget = context.ctarget
  trymodeprob = (ctarget.size_base-ctarget.size)/ctarget.size_base
  resolve_targetting_event(context, bv, narrator, "trymode_status_bot", trymodeprob,
                           _trymode_activation_success)

