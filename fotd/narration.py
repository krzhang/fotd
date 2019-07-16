import random

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
  
  def chara_narrate(self, character, text, **context):
    self.view.disp_chara_speech(character, text, **context)

class BattleNarrator(Narrator):

  def __init__(self, battle, battleview):
    super().__init__(battleview)
    self.battle = battle
    self.battle.narrator = self
  
  def unit_speech(self, unit, text, **context):
    # Han factor:
    if "Han" in unit.name and "Xu" in unit.name and random.random() < 0.50:
      self.chara_narrate(unit.character, "Bruh.", **context)
    else:
      self.chara_narrate(unit.character, text, **context)

  # the lack of symmetry here annoys me

  STATUS_DEFAULTS = {
    "on_receive":"{ctarget} is now {stat_str}",
    "on_remove":"{ctarget} is no longer {stat_str}",
    "on_retain":"{ctarget} is still {stat_str}",
  }

  def narrate_formations(self):
    for i in [0, 1]:
      form = self.battle.formations[i]
      self.view.yprint(rps.formation_info(str(form), "desc"),
                       templates={"ctarget_army":self.battle.armies[i]})

  def narrate_commitment_guarantee(self, key, **context):
    """
    Used to narrate the perfect rolls
    """
    self.view.disp_activated_narration(ROLLS[key]['short'], "guaranteed!", True)
      
  def narrate_status(self, key, **context):
    ctarget = context["ctarget"]
    stat_str = context["stat_str"]
    if key in status.STATUSES[stat_str]:
      if status.STATUSES[stat_str][key] is None: # user says to not do anything
        return
      else:
        self.view.yprint(status.status_info(stat_str, key), templates=context)
    else:
      # use a default
      self.view.yprint(BattleNarrator.STATUS_DEFAULTS[key], templates=context)

  def narrate_roll_success(self, key, success, **context):
    """
    Narrates speeches that happen when a roll succeeds or fails.
    """
    if success:
      narrator_str, narrate_text = get_one(ROLLS[key], "on_success_speech")
      if key == 'fire_tactic':
        graphics_asciimatics.render_fire_tactic()
      if key == 'panic_tactic':
        graphics_asciimatics.render_panic_tactic() 
      if key == 'flood_tactic':
        graphics_asciimatics.render_flood_tactic() 
    else:
      narrator_str, narrate_text = get_one(ROLLS[key], "on_fail_speech")
    if narrator_str and (narrator_str in context) and narrate_text:
      self.unit_speech(context[narrator_str], narrate_text, **context)

  def narrate_roll_post_success(self, key, success, **context):
    """
    This is just a signifier that happens after the roll and the resolution.
    Ex: <MAD_SKILL> Success!
    """
    if ROLLS[key]['show_roll_success']:
      self.view.disp_activated_narration(ROLLS[key]['short'], "", success)
      
  def _narrate_jeer(self, success, **context):
    # after rolling, always make 2 narrations
    if random.random() < 0.50:
      # monkey island style
      ins = random.choice(insults.INSULTS_PAIRS)
      narration0 = (context["csource"], ins[0])
      if success:
        # no good comeback
        narration1 = (context["ctarget"], "Uh, um...")
      else:
        narration1 = (context["ctarget"], ins[1])
    else:
      # roguelike style
      narration0 = (context["csource"],
                    "You are a {}!".format(insults.random_diss()))
      if success:
        narration1 = (context["ctarget"],
                      "Uh, um...")
      else:
        narration1 = (context["ctarget"],
                      "Well, you are a {}!".format(insults.random_diss()))
    self.unit_speech(narration0[0], narration0[1], **context)
    self.unit_speech(narration1[0], narration1[1], **context)
    graphics_asciimatics.render_jeer_tactic(narration0, narration1)

  def narrate_roll(self, key, success, **context):
    if "on_roll" in ROLLS[key] and ROLLS[key]["on_roll"]:  # need both so you don't format None
      # normal situation
      self.view.yprint(get_one(ROLLS[key], "on_roll"), templates=context)
      # self.view.disp_activated_narration(get_one(ROLLS[key], "short"), on_roll)
    if key == "jeer_tactic":
      self._narrate_jeer(success, **context)
    self.narrate_roll_success(key, success, **context)

ENTRANCES = [
  "It's a good day for a battle.",
  "War... what is it good for?",
  "We should not underestimate our opponents.",
  "Hahah! They don't stand a chance!",
  "It does not look like an easy battle...",
  "I am a bit worried about {strong_opponent}, let's take caution.",
  "Well, it is time."
]

WITHDRAWS = [
  "Of the 36 tactics, running is the best one.",
  "Seems we are bested, but we will pay it back later with interest.",
  "Not going to stay around for a losing battle. Next time!",
  "Win some, lose some."]

CAPTURES = [ "Wow. That really happened.",
            "Did not think I would be captured...",
            "Win some, lose some.",
            "I wasn't trying, so does it count?"]

ROLLS = {
  "lure_tactic": {
    "roll_type": 'targetted tactic',
    "short": 'lure',
    "on_success": "{lurer} $[2]$lures$[7]$ {ctarget} into {csource}'s tactic!",
    "on_success_speech": [("lurer", "Here, kitty kitty kitty...")],
    "show_roll_success": False,
  },

  "fire_tactic": {
    "roll_type": 'targetted tactic',
    "short": 'fire',
    "on_roll": ["{csource} prepares embers and tinder..."],
    "on_success_speech": [("csource", "It's going to get pretty hot!"),
                          ("ctarget", "Oh no! My soldiers are engulfed in flames!")],
    "on_fail_speech": [("csource", "{ctarget} did not fall for my tricks."),
                       ("ctarget", "No need to play with fire, {csource}!")],
    "show_roll_success": True,
  },
  "jeer_tactic": {
    "roll_type": 'targetted tactic',
    "short": 'jeer',
    "on_roll": ["{csource} prepares their best insults..."],
    # "on_success_speech":  [("csource", "{ctarget}'s soldiers are fuming to fight."),
    #                        ("ctarget", "Why you...")],
    # "on_fail_speech": [], # has its own routine
    "show_roll_success": True,
  },
  "lure_tactic": {
    "roll_type": 'targetted tactic',
    "short": 'lure',
    "on_roll": None,
    "on_success": "{lurer} $[2]$lures$[7]$ {ctarget} into the tactic!",
    "on_success_speech": [("lurer", "Here, kitty kitty kitty...")],
    "on_fail_speech": None, # has its own routine
    "show_roll_success": False,
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
  },
  "trymode_status_bot": {
    "roll_type": 'buff',
    "short": 'trymode',
    "on_roll": ["{ctarget} looks for an excuse to pretend to be powered up..."],
    "on_success_speech": [("ctarget", "Did you really think I took you seriously before?"),
                          ("ctarget", "*Yawn* Let's get it.")],
    "on_fail_speech": [("ctarget", "Nope, still not trying."),
                       ("ctarget", "I have not yet begun to fight.")],
    "show_roll_success": True,
  },
}
