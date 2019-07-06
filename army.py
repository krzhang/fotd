import skills
import status
import textutils
from textutils import Colors

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
    self.skills = [skills.Skill(s) for s in skillstrs if s in skills.SKILLS_IMPLEMENTED]
    self.health = 100
    self.items = []
    self.status = []
    self.calc_attributes()
    self.color = ""

  def __eq__(self, other):
    return self.id == other.id
    
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
    self.targetting = None
    self.attacked = [] # enemies attacked in a turn
    self.attacked_by = []

  def __eq__(self, other):
    return self.character == other.character
    
  def __repr__(self):
    return repr(self.character)

  def size_repr(self):
    csize = self._size_single_repr(self.size) + str(self.size) + Colors.ENDC
    return "{: <2}/{: <2}".format(str(csize), str(self.size_base))
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

  def has_unit_status(self, stat_str):
    return stat_str in [s.stat_str for s in self.unit_status]
  
  def add_unit_status(self, stat_str):
    """ as strings. DON'T USE WITH SKILLS """
    if not self.has_unit_status(stat_str):
      self.unit_status.append(status.Status(stat_str))

  def remove_unit_status(self, statstr):
    #import pdb; pdb.set_trace()
    #self.unit_status = [s for s in self.unit_status if s.stat_str != statstr]
    self.unit_status.remove(status.Status(statstr))
    
  def attack_strength(self, dmg_type):
    dam = float(self.size)/2
    if dmg_type == "DMG_ARROW":
      dam /= 2
    if self.has_unit_status("trymode_activated"):
      dam *= 1.5
    return float(dam)

  def defense_strength(self, dmg_type):
    de = float(self.size)
    if dmg_type == "DMG_ARROW":
      # arrow damage shouldn't scale with numbers
      de = 10.0
    if self.has_unit_status("defended"):
      de *= 1.5
    if self.has_unit_status("trymode_activated"):
      de *= 1.5
    return float(de*1.5)      

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
