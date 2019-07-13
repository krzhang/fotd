import status

class Narrator():
  """
  A kind of mid-level renderer for rendering narrations by characters.
  """

  def __init__(self, view):
    self.view = view
  
  def chara_narrate(self, character, text):
    self.view.disp_chara_speech(character, text)

class BattleNarrator(Narrator):

  def __init__(self, battle, battleview):
    super().__init__(battleview)
    self.battle = battle
  
  def unit_speech(self, unit, text, **kwargs):
    self.chara_narrate(unit.character, text)


  # the lack of symmetry here annoys me

  STATUS_DEFAULTS = {
    "on_receive":"{ctarget} is now {stat_str}",
    "on_remove":"{ctarget} is no longer {stat_str}",
    "on_retain":"{ctarget} is still {stat_str}",
  }
  
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
  "Not going to stay around for a losing battle. Next time!"
  "Win some, lose some."
]

CAPTURES = [ "Wow. That really happened.",
            "Did not think I would be captured...",
            "Win some, lose some.",
            "I wasn't trying, so does it count?"
]

