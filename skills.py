from textutils import Colors, yprint

def _success_color(success):
  if success:
    return Colors.OKGREEN
  elif success == False:
    return Colors.MAGENTA
  else:
    # when we don't know if it failed
    return Colors.GREEN

class Skill(object):

  def __init__(self, skill_str):
    self.skill_str = skill_str

  def __str__(self):
    return self.skill_str
  
  def __eq__(self, other):
    # this allows us to e.g. remove
    return self.skill_str == other.skill_str
  
  def activation_str(self, success=None):
    return "<" + _success_color(success) + " ".join(self.skill_str.upper().split("_")) + Colors.ENDC + ">"

  def __repr__(self):
    return "<" + Colors.GREEN + self.skill_str + Colors.ENDC + ">"
  
  def narrate(self, otherstr):
    yprint("  " + self.activation_str() + " " + otherstr)

def skill_narration(skill_str, other_str, success=None):
  if success:
    successtr = "SUCCESS!"
  else:
    successtr = "FAIL!"
  if other_str == "":
    other_str = _success_color(success) + successtr + Colors.ENDC
  yprint(Skill(skill_str).activation_str(success) + " " + other_str)

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
    "desc": "Each time this officer is shot by arrows, he/she has a chance to shoot back."
  },
  "chu_ko_nu": {
    "ai_eval": (1,0,1),
  },
  "attack_supplies": {
    "ai_eval": (0,0,1),
    "desc": "This officer is skilled at attacking the enemy's supplies and foiling their support, which disrupts the enemy logistics and morale."
  },
  "panic_tactic": {
    "ai_eval": (0,0,2),
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
    "on_roll": ["{csource} prepares embers and tinder..."],
    "on_success_speech": [("csource", "It's going to get pretty hot!"),
                          ("ctarget", "Oh no! My soldiers are engulfed in flames!")],
    "on_fail_speech": [("csource", "{ctarget} did not fall for my tricks."),
                       ("ctarget", "No need to play with fire, {csource}!")],    
  },
  "lure": {
    "ai_eval": (0,0,1),
    "on_success": "{lurer} " + Colors.GREEN + "lures " + Colors.ENDC + "{ctarget} into the tactic!",
    "on_success_speech": [("lurer","Here, kitty kitty kitty...")],
  },
  "jeer": {
    "ai_eval": (0,0,2)
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
    "ai_eval": (3,0,0)
  },
  "water_tactic": {
    "ai_eval": (0,0,1),
    "on_roll": ["{csource} positions dams and ships..."],
    "on_success_speech": [("csource", "Oh my. This is going to be painful."),
                          ("csource", "The Gods of nature are unforgiving.")],
    "on_fail_speech": [("csource", "{ctarget} narrowly avoided being swept away."),
                       ("ctarget", "No need to play with fire, {csource}!")],    
    
  }
}

