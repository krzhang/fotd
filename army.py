import skills
import status
from textutils import Colors

STAT_BASES = {"power":"power_base",
              "intel":"intel_base",
              "pol":"pol_base",
              "cha":"cha_base"}

class Character(object):
  def __init__(self, name, title, power, intel, pol, cha, coolness, bravery, skillstrs):
    self.name = name
    self.title = title
    self.power_base = power
    self.intel_base = intel
    self.pol_base = pol
    self.cha_base = cha
    self.coolness_base = coolness
    self.bravery_base = bravery
    self.skills = [skills.Skill(s) for s in skillstrs if s in skills.SKILLS_IMPLEMENTED]
    self.health = 100
    self.items = []
    self.status = []
    self.calc_attributes()
    self.color = ""
    
  def calc_attributes(self):
    for s in STAT_BASES:
      setattr(self, s, STAT_BASES[s])
    # do items stuff

  def equip(self, item):
    self.items.append(item)
    self.calc_attributes()

  def narrate(self, otherstr):
    """When this character says something """
    print("  " + repr(self) + ": '" + Colors.GREEN + otherstr + Colors.ENDC + "'")
    
  def __repr__(self):
    if self.title:
      titlestr = " -=" + Colors.YELLOW + self.title + Colors.ENDC + "=-"
    else:
      titlestr = ""
    return str(self) + titlestr

  def __str__(self):
    return self.color + self.name + Colors.ENDC
  
class Unit(object):
  def __init__(self, character, size, speed):
    self.character = character
    self.name = character.name
    self.size_base = size
    self.size = size
    self.speed = speed
    self.armyid = None
    self.unit_status = [] # not to be confused with character-status
    
  def __repr__(self):
    return repr(self.character)

  def size_repr(self):
    csize = self._size_single_repr(self.size) + str(self.size) + Colors.ENDC
    return "{size1: >2}/{size2: >2}".format(size1=csize, size2=self.size_base)
    strb = "{}".format(self.size) + Style.RESET_ALL
    strc = "/{}, speed: {})".format(self.size_base, self.speed)

  def status_real_repr(self):
    return " ".join((str(s) for s in self.unit_status if not s.is_skill()))

  def set_color(self, color):
    self.character.color = color
  
  def __str__(self):
    return str(self.character)

  def _size_single_repr(self, size):
    if size >= 0.66*self.size_base:
      return Colors.GREEN
    elif size >= 0.33*self.size_base:
      return Colors.YELLOW
    else:
      return Colors.RED
  
  # def add_skill(self, skillstr):
  #   """ as strings """
  #   self.character_skills.append(skills.Skill(skillstr))

  # def has_skill(self, skill):
  #   return skill in self.character.skills
    
  # def remove_skill(self, skillstr):
  #   self.character_skills.remove(skills.Skill(skillstr))

  def narrate(self, otherstr):
    """ When we need him to say something """
    self.character.narrate(otherstr)

  def has_unit_status(self, statstr):
    return statstr in [s.stat_str for s in self.unit_status]
  
  def add_unit_status(self, statstr):
    """ as strings. DON'T USE WITH SKILLS """
    self.unit_status.append(status.Status(statstr))

  def remove_unit_status(self, statstr):
    #import pdb; pdb.set_trace()
    #self.unit_status = [s for s in self.unit_status if s.stat_str != statstr]
    self.unit_status.remove(status.Status(statstr))
    
  def attack_strength(self):
    size = self.size
    if self.has_unit_status("trymode_activated"):
      size *= 1.5
    return int(size)

  def defense_strength(self):
    size = self.size
    if self.has_unit_status("defended"):
      size *= 1.5
    if self.has_unit_status("trymode_activated"):
      size *= 1.5
    return int(size)      

  def is_defended(self):
    return self.has_unit_status("defended")
  
  def is_alive(self):
    return self.size > 0 and self.character.health > 0

class Army(object):
  def __init__(self, name, units, armyid, color):
    self.name = name
    self.units = units
    self.color = color
    self.armyid = armyid
    for u in units:
      u.armyid = armyid
      u.set_color(color)

  def is_alive(self):
    return any([u for u in self.units if u.is_alive()])

  def live_units(self):
    return [u for u in self.units if u.is_alive()]

  def str_estimate(self):
    return sum([u.size for u in self.units], 0)