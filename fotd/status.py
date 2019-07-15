from colors import Colors, ctext
import skills

STATUSES = {}

class Status(object):

  def __init__(self, stat_str):
    self.stat_str = stat_str

  def __eq__(self, other):
    # this allows us to e.g. remove
    return self.stat_str == other.stat_str

  def __str__(self):  # todo: move out
    if "viz" in STATUSES[self.stat_str]:
      return STATUSES[self.stat_str]["viz"]
    else:
      return ctext(self.stat_str, Colors.FAILURE)

  def __repr__(self):
    return self.stat_str

  def is_skill(self):
    return self.stat_str in skills.SKILLS
#    return self.stat_str.endswith("_STATUS") and self.stat_str[:-7] in skill.Skill.SKILLS

def status_info(status_str, key):
  """ Main auxiliary function; gets a piece of info about a status type, return None otherwise """
  if (status_str in STATUSES) and (key in STATUSES[status_str]):
    return STATUSES[status_str][key]
  return None

  # @classmethod
  # def FromSkillName(cls, skillstr):
  #   return cls(skillstr + "_STATUS", skill_str=skillstr)

STATUSES_BATTLE = {
  # "berserk": {
  #   "eot":("remove_status_probabilistic", {"fizzle_prob":0.8}),
  #   "on_receive": "{ctarget}'s units fall into a confused rage and is now {stat_viz}!",
  #   "on_remove": "{ctarget} regains control.",
  #   "viz":Colors.RED + "bErSeRk" + Colors.ENDC
  # },
  "burned": {
    "bot":("burned_bot", {}), # these are length 1, but maybe do variable length eventually
    # this means "bot_func" will have a link to the actual function burn_bot
    "eot":("burned_eot", {}),
    "on_receive": "{ctarget} bursts into flames and is now {stat_viz}!",
    "on_remove": "{ctarget} has put out the fire.",
    "on_retain": "The fire burning {ctarget} rages on.",
    "viz":'$[1]$b$[3]$u$[1]$r$[3]$n$[1]$i$[3]$n$[1]$g$[7]$',
  },
  "panicked": {
    "eot":("remove_status_probabilistic", {"fizzle_prob":0.5}),
    "on_receive": "{ctarget}'s unit collapses into a chaotic {stat_viz} state!",
    "on_order_override": "{ctarget}'s unit is $[3]$panicked$[7]$ and $[4]$defends$[7]$, ignoring orders.",
    "on_remove": "{ctarget} regains control.",
  },
  "provoked": {
    "eot":("remove_status_probabilistic", {"fizzle_prob":0.25}),
    "on_order_override": "{ctarget}'s unit is $[1]$provoked$[7]$ and $[1]$marches$[7]$, ignoring orders.",
    "on_receive": "{ctarget}'s units are {stat_viz}; they are angry and out of control!",
    "on_remove": "{ctarget} regains control.",
    "viz":"$[1]$provoked$[7]$",
  },
  "defended": {
    "eot":("remove_status_probabilistic", {"fizzle_prob":1.1}), # round up for floating error
    # "on_receive": "{target} is now {stat_viz} against standard tactics",
    "on_receive": None,
    "on_remove": None
  },
  "is_commander": {
    "viz":"$[3]$commander$[7]$",
  },
  "trymode_activated": {
    # "eot":[],
    "on_receive": "{ctarget} is actually trying now; they are brimming with power.",    
    "on_remove": None
  },
  "received_physical_attack": {
    "eot":("remove_status_probabilistic", {"fizzle_prob":1.1}),
    "on_remove": None
  }
}

# these are statuses that are just about having skills, not about activating them
STATUSES_FROM_SKILLS = {
  "trymode": {
    "bot":("trymode_status_bot", {})
  }
}

STATUSES = dict(list(STATUSES_BATTLE.items()) +
                list(STATUSES_FROM_SKILLS.items()))

