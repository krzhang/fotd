"""
The main thing we expose is Statuses, which is a dictionary [str]:[Status object]
"""

from colors import ctext
import skills

# the RAW dictionaries are just plain text
STATUSES_BATTLE_RAW = {
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
    "on_activation": "{ctarget} is $[3]$panicked!$[7]$! No action.",
    "on_remove": "{ctarget} regains control.",
  },
  "provoked": {
    "eot":("remove_status_probabilistic", {"fizzle_prob":0.25}),
    "on_receive": "{ctarget}'s units are {stat_viz}; they are angry and out of control!",
    "on_remove": "{ctarget} regains control.",
    "viz":"$[1]$provoked$[7]$",
  },
  "defended": {
    "eot":("remove_status_probabilistic", {"fizzle_prob":1.1}), # round up for floating error
    # "on_receive": "{ctarget}: staying put, {stat_viz};",
    "on_receive": None,
    "on_remove": None,
  },
  "is_commander": {
    "viz":"$[3]$commander$[7]$",
  },
  "trymode_activated": {
    # "eot":[],
    "on_receive": "{ctarget} is actually trying now; they are brimming with power.",    
    "on_remove": None,
    "viz":"$[2,1]$tRyInG$[7]$",
  },
  "received_physical_attack": {
    "eot":("remove_status_probabilistic", {"fizzle_prob":1.1}),
    "on_remove": None
  }
}

# these are statuses that are just about having skills, not about activating them
STATUSES_SKILLS_RAW = {
  "trymode": {
    "bot":("trymode_status_bot", {})
  }
}

STATUSES_RAW = dict(list(STATUSES_BATTLE_RAW.items()) +
                    list(STATUSES_SKILLS_RAW.items()))

class Status(object):

  def __init__(self, stat_str):
    self.stat_str = stat_str
    self.bot = (None, {})
    self.eot = (None, {})
    self.on_receive = None
    self.on_remove = None
    self.on_retain = None
    self.viz = None
    if stat_str in STATUSES_RAW and STATUSES_RAW[stat_str]:
      for key in STATUSES_RAW[stat_str]:
        setattr(self, key, STATUSES_RAW[stat_str][key])

  def __eq__(self, other):
    # this allows us to e.g. remove
    return self.stat_str == other.stat_str

  def __str__(self):
    return self.stat_str

  def __repr__(self):
    return self.stat_str

  def stat_viz(self):
    if self.viz:
      return self.viz
    else:
      return ctext(self.stat_str, "$[3]$")

  def is_skill(self):
    return self.stat_str in skills.SKILLS
#    return self.stat_str.endswith("_STATUS") and self.stat_str[:-7] in skill.Skill.SKILLS

# def status_info(status_str, key):
#   """ Main auxiliary function; gets a piece of info about a status type, return None otherwise """
#   if (status_str in STATUSES) and (key in STATUSES[status_str]):
#     return STATUSES[status_str][key]
#   return None

STATUSES = {s:Status(s) for s in STATUSES_RAW}
