from colors import success_color

class Skill(object):

  def __init__(self, skill_str):
    self.skill_str = skill_str

  def __str__(self):
    return self.skill_str
  
  def __eq__(self, other):
    # this allows us to e.g. remove
    return self.skill_str == other.skill_str
  
  def __repr__(self):
    return "<$[2$]" + self.skill_str + "$[7$]>"
  
  def short(self):
    return "<$[2$]" + info(self.skill_str, "short") + "$[7$]>"

def info(skill_str, key):
  if key in SKILLS[skill_str]:
    return SKILLS[skill_str][key]
  return None

SKILLS = {
  "chaos_arrow": {
    "ai_eval": (1,0,1),
    "desc": "A devastating skill that unleashes arrows at all enemy combatants. Used when attacking."
  },
  "counter_arrow": {
    "ai_eval": (2,1,1),
    "desc": "Each time this officer is shot by arrows, he/she has a chance to shoot back.",
    "short": 'ctr-a',
  },
  "chu_ko_nu": {
    "ai_eval": (1,0,1),
    "short": 'c-k-n'
  },
  "attack_supplies": {
    "ai_eval": (0,0,1),
    "desc": "This officer is skilled at attacking the enemy's supplies and foiling their support, which disrupts the enemy logistics and morale."
  },
  "panic_tactic": {
    "ai_eval": (0,0,2),
    "short": 'panic',
    "on_roll": ["{csource} sows seeds of fear and doubt in {ctarget}'s unit..."],
    "on_success_speech": [("csource", "{ctarget} will be out of commission for a while..."),
                          ("ctarget", "The soldiers are incredibly scared, of everything from spies to ghosts.")],
    "on_fail_speech": [("csource", "{ctarget}'s unit was not shaken."),
                       ("ctarget", "Keep calm, don't let {csource}'s trickery get to you.")],    
  },
  "cheer": {
    "ai_eval": (0,1,1)
  },
  "fire_tactic": {
    "ai_eval": (0,0,1),
    "short": 'fire',
    "on_roll": ["{csource} prepares embers and tinder..."],
    "on_success_speech": [("csource", "It's going to get pretty hot!"),
                          ("ctarget", "Oh no! My soldiers are engulfed in flames!")],
    "on_fail_speech": [("csource", "{ctarget} did not fall for my tricks."),
                       ("ctarget", "No need to play with fire, {csource}!")],    
  },
  "lure": {
    "ai_eval": (0,0,1),
    "short": 'lure',
    "on_success": "{lurer} $[2$]lures$[7$] {ctarget} into the tactic!",
    "on_success_speech": [("lurer","Here, kitty kitty kitty...")],
  },
  "jeer": {
    "ai_eval": (0,0,2),
    "short": 'jeer'
  },
  "manuever": {
    "ai_eval": (1,0,1)
  },
  "mushou": {
    "ai_eval": (1,2,0)
  },
  "perfect_defense": {
    "ai_eval": (0,2,0)
  },
  "pincer_specialist": {
    "ai_eval": (2,1,0)
  },
  "trymode": {
    "ai_eval": (3,0,0),
    "short": 'trym'
  },
  "water_tactic": {
    "ai_eval": (0,0,1),
    "short": 'water',
    "on_roll": ["{csource} positions dams and ships..."],
    "on_success_speech": [("csource", "Oh my. This is going to be painful."),
                          ("csource", "The Gods of nature are unforgiving.")],
    "on_fail_speech": [("csource", "{ctarget} narrowly avoided being swept away."),
                       ("ctarget", "No need to play with fire, {csource}!")],    
    
  }
}

