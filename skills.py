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

SKILLS_IMPLEMENTED = ["counter_arrow",
                      "chu_ko_nu",
                      "panic_tactic",
                      "fire_tactic",
                      "jeer",
                      "trymode",
                      "water_tactic"]

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
    "ai_eval": (0,0,2)
  },
  "cheer": {
    "ai_eval": (0,1,1)
  },
  "fire_tactic": {
    "ai_eval": (0,0,1)
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
    "ai_eval": (0,0,1) 
  }
}

