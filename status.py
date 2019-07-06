from textutils import Colors, yprint
import skills

STATUSES = {}

class Status(object):
  
  def __init__(self, stat_str):
    self.stat_str = stat_str

  def __eq__(self, other):
    # this allows us to e.g. remove
    return self.stat_str == other.stat_str
  
  def __str__(self):
    if "viz" in STATUSES[self.stat_str]:
      return STATUSES[self.stat_str]["viz"]
    else:
      return Colors.RED + self.stat_str + Colors.ENDC

  def __repr__(self):
    return self.stat_str
  
  def is_skill(self):
    return self.stat_str in skills.SKILLS
#    return self.stat_str.endswith("_STATUS") and self.stat_str[:-7] in skill.Skill.SKILLS

  def run_status_func(self, func_key, context):
    ss = self.stat_str
    # import pdb;pdb.set_trace()
    if ss in STATUSES and func_key + '_func' in STATUSES[ss]:
      STATUSES[ss][func_key+'_func'](context.copy(additional_opt={"status":ss}))

  # @classmethod
  # def FromSkillName(cls, skillstr):
  #   return cls(skillstr + "_STATUS", skill_str=skillstr)

STATUSES_BATTLE = {
  "berserk": {
    "eot":["berserk_eot"],
    "on_receive": "{target}'s units fall into a confused rage and is now {stat_viz}",
    "viz":Colors.RED + "bErSeRk!!!" + Colors.ENDC
  },
  "burned": {
    "bot":["burned_bot"], # these are length 1, but maybe do variable length eventually
    # this means "bot_func" will have a link to the actual function burn_bot
    "eot":["burned_eot"],
    "on_receive": "{target} bursts into flames and is now {stat_viz}",
    "viz":Colors.RED+'b'+Colors.YELLOW+'u'+Colors.RED+'r'+Colors.YELLOW+'n'+Colors.RED+'i'+Colors.YELLOW+'n'+Colors.RED+'g'+Colors.ENDC
  },
  "panicked": {
    "eot":["panic_eot"],
    "on_receive": "{target}'s unit collapses into a chaotic {stat_viz} state",
  },
  "defended": {
    "eot":["generic_eot_fizzle"],
    "on_receive": "{target} is now {stat_viz} against standard tactics",    
  },
  "trymode_activated": {
    "eot":["generic_eot_fizzle"],
    "on_receive": "{target} is actually trying now; they are brimming with power",    
  }
}
  
STATUSES_FROM_SKILLS = {
  "trymode": {
    "bot":["trymode_status_bot"]
  } 
}

STATUSES = dict(list(STATUSES_BATTLE.items()) +
                list(STATUSES_FROM_SKILLS.items()))
