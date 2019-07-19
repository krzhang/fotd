import random

import duel
import insults
import rps
import status
import graphics_asciimatics

def get_one(dictionary, key):
  """
  Get a narration pair (narrator, text)
  If there is only one choice, get that. Else be random.
  """
  if key not in dictionary or not dictionary[key]:
    return (None, None)
  if type(dictionary[key]) == list:
    return random.choice(dictionary[key])
  else:
    return dictionary[key]

class Narrator():
  """
  A kind of mid-level renderer for rendering narrations by characters.
  """

  def __init__(self, view):
    self.view = view
  
  def chara_narrate(self, character, text, context):
    self.view.disp_chara_speech(character, text, context)

class BattleNarrator(Narrator):

  def __init__(self, battle, battleview):
    super().__init__(battleview)
    self.battle = battle
    self.battle.narrator = self

  def narrate_pair(self, unit, text, context):
    """
    If unit is a character, do a speech. Else do a straight narration
    """
    # Han factor:
    if unit:
      if "Han" in unit.name and "Xu" in unit.name and random.random() < 0.50:
        self.chara_narrate(unit.character, "Bruh.", context)
      else:
        self.chara_narrate(unit.character, text, context)
    else:
      # straight narration
      self.view.yprint(text, templates=context)

  def notify(self, event, *args):
    """
    an event pinged us; 
    1) first, we look in the dictionary.
    2)   If it says "None", do nothing
    3)   it better be a list of 2-tuples. Pick one randomly
    4) Even on success, see if we defined a function called narrate_[event_name], 
       and run it
    """
    event_name = event.event_name
    context = event.context
    if event_name in EVENT_NARRATIONS:
      # don't use dict.get() here since we do a different thing on the two possible Nones
      result = EVENT_NARRATIONS[event_name]
      if result is None:
        pass
      assert type(result) == list
      result_choice = random.choice(result)
      assert type(result_choice) == tuple and len(result_choice) == 2
      if result_choice[0] is None: # straight narration
        speaker = None
      else:
        speaker = context[result_choice[0]]
      self.narrate_pair(speaker, result_choice[1], context)
    # always run the function if you have one
    func = getattr(self, "narrate_" + event_name, None)
    if func is None:
      pass
    else:
      func(context, *args)
      
  # the lack of symmetry here annoys me

  STATUS_DEFAULTS = {
    "on_receive":"{ctarget} is now {stat_str}",
    "on_remove":"{ctarget} is no longer {stat_str}",
    "on_retain":"{ctarget} is still {stat_str}",
  }

  def narrate_formations(self):
    self.view.yprint("", mode=["huddle"])
    for i in [0, 1]:
      form = self.battle.formations[i]
      # print both into the main event buffer and the huddle buffer
      self.view.yprint(rps.formation_info(str(form), "desc"),
                       templates={"ctarget_army":self.battle.armies[i]}, mode=["console","huddle"])
      self.view.yprint("  " + rps.formation_info(str(form), "desc_bonus"),
                       templates={"ctarget_army":self.battle.armies[i]}, mode=["huddle"])
    self.view.yprint("", mode=["huddle"])
    #  self.view._flush()  # so we don't see formations again next time

  def narrate_orders(self, winner_id):
    self.view.yprint("", mode=["huddle"])
    for i in [0, 1]:
      order = self.battle.orders[i]
      # print both into the main event buffer and the huddle buffer
      order_str = rps.order_info(str(order), "desc")
      if not self.battle.armies[i].commitment_bonus:
        order_str = "Breaking formation, " + order_str 
      self.view.yprint(order_str,
                       templates={"ctarget_army":self.battle.armies[i]}, mode=["huddle"])
      if i == winner_id:
        self.view.yprint("  " + rps.order_info(str(order), "yomi_bonus"),
                         templates={"ctarget_army":self.battle.armies[i]}, mode=["huddle"])
        if self.battle.armies[i].commitment_bonus:
          self.view.yprint("  commitment bonus: " + rps.order_info(str(order), "commitment_bonus"),
                         templates={"ctarget_army":self.battle.armies[i]}, mode=["huddle"])
    self.view.yprint("", mode=["huddle"])

  def narrate_march(self, context):
    csource = context.csource
    ctarget = context.ctarget
    # if ctarget in csource.attacked_by:
    if csource.attacked_by:
      # this replication of logic is annoying; the right todo is to have the origional thing
      # emit an event right here, and render at the beginning of that event as opposed to here
      return
    if ctarget.is_defended():
      readytext = "$[2]$defended!$[7]$"
    else:
      readytext = ctarget.str_targetting()
    self.view.yprint("{} ({}) marches into {} ({})".format(csource.color_name(),
                                                           csource.str_targetting(),
                                                           ctarget.color_name(),
                                                           readytext), debug=True)

  def narrate_indirect_raid(self, context):
    csource = context.csource
    ctarget = context.ctarget
    if csource.attacked_by:
      return
    self.view.yprint("{} ({}) sneaks up on {} ({})".format(csource.color_name(),
                                                           csource.str_targetting(),
                                                           ctarget.color_name(),
                                                           ctarget.str_targetting()),
                     debug=True)

  def narrate_status(self, key, context):
    ctarget = context.ctarget
    stat_str = context['stat_str']
    if key in status.STATUSES[stat_str]:
      if status.STATUSES[stat_str][key] is None: # user says to not do anything
        return
      else:
        self.view.yprint(status.status_info(stat_str, key), templates=context)
    else:
      # use a default
      self.view.yprint(BattleNarrator.STATUS_DEFAULTS[key], templates=context)

  def narrate_roll_success(self, context, key, success, commitment_guarantee):
    """
    Narrates speeches that happen when a roll succeeds or fails.
    """
    if commitment_guarantee:
      self.view.disp_activated_narration(ROLLS[key]['short'], "guaranteed!", True)
    if success:
      narrator_str, narrate_text = get_one(ROLLS[key], "on_success_speech")
      if not self.view.automated:
        if 'graphics_renderer' in ROLLS[key]:
          getattr(graphics_asciimatics, ROLLS[key]['graphics_renderer'])()
      if key == 'chu_ko_nu':
        if random.random() < 0.5 and context.csource.name == "Zhuge Liang":
          narrator_str = 'The name is a bit embarassing...'
    else:
      narrator_str, narrate_text = get_one(ROLLS[key], "on_fail_speech")
    if narrator_str and (narrator_str in context) and narrate_text:
      self.narrate_pair(context[narrator_str], narrate_text, context)

  def narrate_roll_post_success(self, context, key, success):
    """
    This is just a signifier that happens after the roll and the resolution.
    Ex: <MAD_SKILL> Success!
    """
    if success and ROLLS[key]['show_roll_success']:
      self.view.disp_activated_narration(ROLLS[key]['short'], "", success)
    if (not success) and ROLLS[key]['show_roll_failure']:
      self.view.disp_activated_narration(ROLLS[key]['short'], "", success)
      
  def _narrate_jeer(self, success, context):
    # after rolling, always make 2 narrations
    if random.random() < 0.50:
      # monkey island style
      ins = random.choice(insults.INSULTS_PAIRS)
      narration0 = (context["csource"], ins[0])
      if success:
        # no good comeback
        narration1 = (context["ctarget"], "...")
      else:
        narration1 = (context["ctarget"], ins[1])
    else:
      # roguelike style
      narration0 = (context["csource"],
                    "You are a {}!".format(insults.random_diss()))
      if success:
        narration1 = (context["ctarget"], "...")
      else:
        narration1 = (context["ctarget"],
                      "Well, you are a {}!".format(insults.random_diss()))
    self.narrate_pair(narration0[0], narration0[1], context)
    self.narrate_pair(narration1[0], narration1[1], context)
    if not self.view.automated:
      # hack: move later
      graphics_asciimatics.render_jeer_tactic(narration0, narration1)

  def narrate_roll(self, key, success, context):
    if "on_roll" in ROLLS[key] and ROLLS[key]["on_roll"]:  # need both so you don't format None
      # normal situation
      self.view.yprint(get_one(ROLLS[key], "on_roll"), templates=context)
      # self.view.disp_activated_narration(get_one(ROLLS[key], "short"), on_roll)
    if key == "jeer_tactic":
      self._narrate_jeer(success, context)
    self.narrate_roll_success(key, success, context)

  # meta stuff: armies leaveing, etc.
  
  def narrate_unit_escaped(self, context):
    self.view.yprint("{ctarget} escapes!", templates=context)

  def narrate_unit_captured(self, context):
    self.view.yprint("{ctarget} was captured!", templates=context)

    
ENTRANCES = [
  "It's a good day for a battle.",
  "War... what is it good for?",
  "We should not underestimate our opponents.",
  "Hahah! They don't stand a chance!",
  "It does not look like an easy battle...",
  "I am a bit worried about {strong_opponent}, let's take caution.",
  "Well, it is time."
]

ROLLS = {
  "fire_tactic": {
    "roll_type": 'targetted tactic',
    "short": 'fire',
    "on_roll": ["{csource} prepares embers and tinder..."],
    "on_success_speech": [("csource", "It's going to get pretty hot!"),
                          ("ctarget", "Oh no! My soldiers are engulfed in flames!")],
    "on_fail_speech": [("csource", "{ctarget} did not fall for my tricks."),
                       ("ctarget", "No need to play with fire, {csource}!")],
    "show_roll_success": True,
    "show_roll_failure": True,
    "graphics_renderer": 'render_fire_tactic',
  },
  "jeer_tactic": {
    "roll_type": 'targetted tactic',
    "short": 'jeer',
    "on_roll": ["{csource} prepares their best insults..."],
    # "on_success_speech":  [("csource", "{ctarget}'s soldiers are fuming to fight."),
    #                        ("ctarget", "Why you...")],
    # "on_fail_speech": [], # has its own routine
    "show_roll_success": True,
    "show_roll_failure": True,
#    "graphics_renderer": 'render_jeer_tactic',
  },
  "lure_tactic": {
    "roll_type": 'targetted tactic',
    "short": 'lure',
    "on_roll": None,
    "on_success": "{lurer} $[2]$lures$[7]$ {ctarget} into the tactic!",
    "on_success_speech": [("lurer", "Here, kitty kitty kitty..."),
                          ("lurer", "Let's bring {ctarget} along too...")],
    "on_fail_speech": None, # has its own routine
    "show_roll_success": False,
    "show_roll_failure": False,
  },  
  "panic_tactic": {
    "roll_type": 'targetted tactic',
    "short": 'panic',
    "on_roll": ["{csource} sows seeds of fear and doubt in {ctarget}'s unit..."],
    "on_success_speech": [("csource", "{ctarget} will be out of commission for a while..."),
                          ("ctarget", "The soldiers are incredibly scared of everything.")],
    "on_fail_speech": [("csource", "{ctarget}'s unit was not shaken."),
                       ("ctarget", "Keep calm, don't let {csource} get to you.")],
    "show_roll_success": True,
    "show_roll_failure": True,
    "graphics_renderer": 'render_panic_tactic',
  },
  "flood_tactic": {
    "roll_type": 'targetted tactic',
    "short": 'flood',
    "on_roll": ["{csource} manipulates the dams..."],
    "on_success_speech": [("csource", "Water is crashing through their ships."),
                          ("csource", "The Gods of nature are unforgiving.")],
    "on_fail_speech": [("csource", "{ctarget} narrowly avoided being swept away."),
                       ("ctarget", "No need to play with fire, {csource}!")],
    "show_roll_success": True,
    "show_roll_failure": True,
    "graphics_renderer": 'render_flood_tactic',
  },
  "counter_arrow": {
    "roll_type": 'targetted tactic',
    "short": 'counter arrow',
    "on_roll": None,
    "on_success_speech": [('csource', "Let's show {ctarget} how to actually use arrows!"),
                          (None, '{csource} counters with their own volley.')],
    "on_fail_speech": None,
    "show_roll_success": False,
    "show_roll_failure": False,    
   },
   "chu_ko_nu": {
    "roll_type": 'targetted tactic',
    "short": 'chu ko nu',
    "on_roll": None,
    "on_success_speech": [("csource", "Have some more!")],
    "on_fail_speech": None,
    "show_roll_success": False,    
    "show_roll_failure": False,    
  },
  "fire_arrow": {
    "roll_type": 'targetted tactic',
    "short": 'fire arrow',
    "on_roll": None,
    "on_success_speech": [("csource", "Let them have a taste of these flaming arrows!")],
    "on_fail_speech": None,
    "show_roll_success": False,
    "show_roll_failure": False,    
  },
  "trymode_status_bot": {
    "roll_type": 'buff',
    "short": 'trymode',
    # "on_roll": ["{ctarget} looks for an excuse to pretend to be powered up..."],
    "on_roll": None,
    "on_success_speech": [("ctarget", "Did you really think I took you seriously before?"),
                          ("ctarget", "*Yawn* Let's get it.")],
    "on_fail_speech": [("ctarget", "Nope, still not trying."),
                       ("ctarget", "I have not yet begun to fight.")],
    "show_roll_success": True,
    "show_roll_failure": False,
  },
}

EVENT_NARRATIONS = {
  "action_already_used": [(None, "{csource} already engaged.",)],
  "physical_clash": [(None, "{csource} clashes against {ctarget}!")],
  "duel_challenged": [
    ('csource', "Is there no one to fight {csource}?"),
    ('csource', "Come {ctarget}, it is a good day for a fight."),
    ('csource', "You are no match for me, {ctarget}."),
    ('csource', "Let's dance, {ctarget}."),
  ],
  "duel_accepted": [
    ('ctarget', "Ahaha, you asked for it!"),
    ('ctarget', "I can beat you with my left hand, {csource}."),
    ('ctarget', "I am surprised you dare to challenge me..."),
    ('ctarget', "{csource}! Exactly who I am waiting for!"),
    ('ctarget', "You know nothing, {csource}."),
  ],
  "duel_rejected": [
    ('ctarget', "A good general does not rely on physical strength alone."),
    ('ctarget', "Maybe another day, {csource}."),
    ('ctarget', "Don't bring playground antics to the battlefield."),
  ],
  "duel_defeated": [
    ('csource', "I bested {ctarget}."),
    ('csource', "I have ninety-nine problems and {ctarget} was not one of them."),
    ('csource', "Enemy down."),
    ('csource', "{ctarget}'s soldiers will now tremble at {csource}'s name."),
    ('csource', "Whew. That was a good warmup."),
    ('csource', "That was a close one."),
  ],
  "panicked_order": [
    (None, "{ctarget}'s unit is $[3]$panicked$[7]$ and $[4]$defends$[7]$, ignoring orders.")],
  "provoked_order": [
    (None, "{ctarget}'s unit is $[1]$provoked$[7]$ and $[1]$marches$[7]$, ignoring orders.")],
  # meta stuff
  "unit_captured": [
    ('ctarget', "Wow. That really happened."),
    ('ctarget', "Did not think I would be captured..."),
    ('ctarget', "I did not think this could happen to me!"),
    ('ctarget', "Win some, lose some."),
    ('ctarget', "I wasn't trying, so does it count?")],
  "unit_escaped": [
    ('ctarget', "Of the 36 tactics, running is the best one."),
    ('ctarget', "Seems we are bested, but we will pay it back later with interest."),
    ('ctarget', "Not going to stay around for a losing battle. Next time!"),
    ('ctarget', "Win some, lose some.")],
  "army_leave_battle": [(None, "{ctarget_army}'s units have all been defeated.")],
  "army_collapse_from_morale": [(None, "{ctarget_army} collapses due to catastrophic morale.")],
}

