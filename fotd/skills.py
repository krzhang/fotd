import random
import colors

class Skill():

  def __init__(self, skill_str):
    self.skill_str = skill_str

  def __str__(self):
    return self.skill_str

  def __eq__(self, other):
    # this allows us to e.g. remove
    return self.skill_str == other.skill_str

  def short(self):
    return skill_info(self.skill_str, "short")

  def str_fancy(self, success=None):
    """
    Ex: < fire >
    """
    return "<" + colors.color_bool(success) + skill_info(self.skill_str, "short") + "$[7]$>"
  
def skill_info(skill_str, key):
  if key in SKILLS[skill_str]:
    return SKILLS[skill_str][key]
  return None

def skillcard_info(skill_str, key):
  if key in SKILLCARDS[skill_str]:
    return SKILLCARDS[skill_str][key]
  return None

def get_skillcard(skill):
  return skill_info(skill.skill_str, "skillcard")

def get_skill_speech(skillstr, key):
  """Give a random speech from a skillcard."""
  return random.choice(skill_info(skillstr, key))

def get_skillcard_speech(skillcard, key):
  """Give a random speech from a skillcard."""
  return random.choice(skillcard_info(skillcard, key))

SKILLS = {
  "chaos_arrow": {
    "ai_eval": (1, 0, 1),
    "desc": "A devastating skill that unleashes arrows at all enemy combatants. Used when attacking.",
    "skillcard": "chaos_arrow",
  },
  "counter_arrow": {
    "ai_eval": (2, 1, 1),
    "desc": "Each time this officer is shot by arrows, he/she has a chance to shoot back.",
    "activation": "passive",
    "short": 'ctr-ar',
  },
  "chu_ko_nu": {
    "ai_eval": (1, 0, 1),
    "rank": 'A',
    "activation": "passive",
    "short": 'c-k-nu'
  },
  "attack_supplies": {
    "ai_eval": (0, 0, 1),
    "desc": "This officer is skilled at attacking the enemy's supplies and foiling their support, which disrupts the enemy logistics and morale."
  },
  "panic_skill": {
    "ai_eval": (0, 0, 2),
    "short": ' panic',
    "skillcard": "panic_tactic",
  },
  "cheer": {
    "ai_eval": (0, 1, 1)
  },
  "fire_skill": {
    "ai_eval": (0, 0, 1),
    "short": ' fire ',
    "skillcard": "fire_tactic",
  },
  "lure_skill": {
    "ai_eval": (0, 0, 1),
    "short": ' lure ',
    "activation": "passive",
  },
  "jeer_skill": {
    "ai_eval": (0, 0, 2),
    "short": ' jeer ',
    "skillcard": "jeer_tactic",
  },
  "manuever": {
    "ai_eval": (1, 0, 1)
  },
  "mushou": {
    "ai_eval": (1, 2, 0),
    "activation": "passive",
  },
  "perfect_defense": {
    "ai_eval": (0, 2, 0),
    "activation": "passive",
  },
  "pincer_specialist": {
    "ai_eval": (2, 1, 0)
  },
  "trymode": {
    "ai_eval": (3, 0, 0),
    "short": ' try-m',
    "activation": "passive",
  },
  "water_skill": {
    "ai_eval": (0, 0, 1),
    "short": ' water',
    "skillcard": "flood_tactic",
  }
}

SKILLCARDS = {
  "fire_tactic": {
    "bulb": {'A':0, 'D':0.15, 'I':0.3},
    "illegal_weather": ["raining"],
    "power": 5,
    "short": ' fire ',
    "skill": "fire_skill",
    "on_bulb": {
      'D': "When they attack, these traps should burn them up.",
      'I': "If they turtle, they are an easy target for fire today.",
    },
    # "on_roll": ["{csource} prepares embers and tinder..."],
    # "on_success_speech": [("csource", "It's going to get pretty hot!"),
    #                       ("ctarget", "Oh no! My soldiers are engulfed in flames!")],
    # "on_fail_speech": [("csource", "{ctarget} did not fall for my tricks."),
    #                    ("ctarget", "No need to play with fire, {csource}!")],
  },
  "jeer_tactic": {
    "bulb": {'A':0.2, 'D':0.2, 'I':0.2},
    "illegal_weather": [],
    "power": 2,
    "short": ' jeer ',
    "skill": "jeer_skill",
    "on_bulb": {
      'A': "Let me at them in the field; I have a few new insults.",
      'D': "If we keep teasing them, they may overattack.",
      'I': "We can go harass them and lure them to fight.",
    },
    # "on_roll": ["{csource} prepares some of their best insults..."],
    # "on_success_speech":  [("csource", "{ctarget}'s soldiers are fuming to fight."),
    #                        ("ctarget", "Why you...")],
    # "on_fail_speech": [], # has its own routine
  },
  "panic_tactic": {
    "bulb": {'A':0.25, 'D':0, 'I':0.25},
    "illegal_weather": [],
    "power": 5,
    "short": ' panic',
    "skill": "panic_skill",
    "on_bulb": {
      'A': "If we attack, I can fill their units with fear.",
      'I': "When they are defending, we can spread rumors and lies.",
    },
    # "on_roll": ["{csource} sows seeds of fear and doubt in {ctarget}'s unit..."],
    # "on_success_speech": [("csource", "{ctarget} will be out of commission for a while..."),
    #                       ("ctarget", "The soldiers are incredibly scared of everything.")],
    # "on_fail_speech": [("csource", "{ctarget}'s unit was not shaken."),
    #                    ("ctarget", "Keep calm, don't let {csource} get to you.")],
  },
  "flood_tactic": {
    "bulb": {'A':0, 'D':0.6, 'I':0},
    "illegal_weather": ["sunny", "hot"],
    "power": 8,
    "short": ' flood',
    "skill": "water_skill",
    "on_bulb": {
      'D': "If they attack near this barely-dammed river...",
    },
    # "on_roll": ["{csource} manipulates the dams..."],
    # "on_success_speech": [("csource", "Water is crashing through their ships."),
    #                       ("csource", "The Gods of nature are unforgiving.")],
    # "on_fail_speech": [("csource", "{ctarget} narrowly avoided being swept away."),
    #                    ("ctarget", "No need to play with fire, {csource}!")],
  },
}
