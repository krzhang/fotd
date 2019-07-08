from colors import Colors
from textutils import yprint
import skills

STAT_BASES = {"power":"power_base",
              "intel":"intel_base",
              "pol":"pol_base",
              "cha":"cha_base"}

class Character(object):
  def __init__(self, name, title, power, intel, pol, cha, coolness, bravery, skillstrs):
    self.id = name + title # this really needs to be rewritten
    self.name = name
    self.title = title
    self.power_base = power
    self.intel_base = intel
    self.pol_base = pol
    self.cha_base = cha
    self.coolness_base = coolness
    self.bravery_base = bravery
    self.skills = [skills.Skill(s) for s in skillstrs]
    self.health = 100
    self.items = []
    self.status = []
    self.calc_attributes()
    self.color = ""

  def __eq__(self, other):
    return hasattr(self, "id") and hasattr(other, "id") and self.id == other.id
    
  def calc_attributes(self):
    for s in STAT_BASES:
      setattr(self, s, STAT_BASES[s])
    # do items stuff

  def equip(self, item):
    self.items.append(item)
    self.calc_attributes()

  def speech(self, otherstr):
    """When this character says something """
    yprint("  " + repr(self) + ": '" + Colors.GREEN + otherstr + Colors.ENDC + "'")
    
  def __repr__(self):
    if self.title:
      titlestr = " -=" + Colors.YELLOW + self.title + Colors.ENDC + "=-"
    else:
      titlestr = ""
    return str(self) + titlestr

  def __str__(self):
    return self.color + self.name + Colors.ENDC
  
