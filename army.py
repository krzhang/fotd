import skills
import status
import intelligence
from colors import Colors

class Unit(object):
  def __init__(self, character, size, speed):
    self.character = character
    self.name = character.name
    self.size_base = size
    self.size = size
    self.speed = speed
    self.armyid = None
    self.is_commander = None
    self.unit_status = [] # not to be confused with character-status
    self.targetting = None
    self.attacked = [] # enemies attacked in a turn
    self.attacked_by = []
    self.position = None
    self.last_turn_size = None
    
  def __eq__(self, other):
    return hasattr(self, "character") and hasattr(other, "character") and self.character == other.character
    
  def __repr__(self):
    return repr(self.character)

  def size_repr(self):
    csize = self._size_single_repr(self.size) + str(self.size) + Colors.ENDC
    return "{}/{}".format(str(csize), str(self.size_base)) 
  
  def status_real_repr(self):
    return " ".join((str(s) for s in self.unit_status if not s.is_skill()))

  def set_color(self, color):
    self.color = color
    self.character.color = color

  def __str__(self):
    return str(self.character)

  def _size_single_repr(self, size):
    if size >= 0.66*self.size_base:
      return Colors.OKGREEN
    elif size >= 0.33*self.size_base:
      return Colors.YELLOW
    else:
      return Colors.RED
  
  def speech(self, otherstr):
    """ When we need him to say something """
    self.character.speech(otherstr)

  def has_unit_status(self, stat_str):
    return stat_str in [s.stat_str for s in self.unit_status]
  
  def add_unit_status(self, stat_str):
    """ as strings. DON'T USE WITH SKILLS """
    if not self.has_unit_status(stat_str):
      self.unit_status.append(status.Status(stat_str))

  def move(self, newpos):
    self.position.remove_unit(self)
    newpos.add_unit(self)
    self.position = newpos
      
  def remove_unit_status(self, statstr):
    #import pdb; pdb.set_trace()
    #self.unit_status = [s for s in self.unit_status if s.stat_str != statstr]
    self.unit_status.remove(status.Status(statstr))
    
  def attack_strength(self, dmg_type):
    dam = float(self.size)/3.5
    if dmg_type == "DMG_ARROW":
      # arrow damage shouldn't scale with numbers
      dam = 2.0
    if self.has_unit_status("trymode_activated"):
      dam *= 1.5
    if self.has_unit_status("burned"):
      dam /= 1.5
    return float(dam)

  def defense_strength(self, dmg_type):
    de = float(self.size)
    if dmg_type == "DMG_ARROW":
      # arrow damage shouldn't scale with numbers
      de = 12.0
    if self.has_unit_status("defended"):
      de *= 1.5
    if self.has_unit_status("trymode_activated"):
      de *= 1.5
    if self.has_unit_status("burned"):
      de /= 1.5
    return float(de*1.5)      

  def is_defended(self):
    return self.has_unit_status("defended")
  
  def is_present(self):
    return self.size > 0 and self.character.health > 0

class Army(object):
  def __init__(self, name, units, armyid, color, intelligence_type):
    self.name = name
    self.units = units
    self.commander = self.units[0]
    self.units[0].is_commander = True
    self.color = color
    self.armyid = armyid
    for u in units:
      u.armyid = armyid
      u.set_color(color)
    self.intelligence_type = intelligence_type
    self.intelligence = intelligence.INTELLIGENCE_FROM_TYPE[intelligence_type]
    self.yomi_edge = None # used in battles to see if RPS was won

  def __repr__(self):
    return "Army({})".format(self.name)

  def str_color(self):
    return "$[{}]{}$[{}]".format(self.color, self.name, 7) # eventually move out  

  def is_present(self):
    return any([u for u in self.units if u.is_present()])

  def present_units(self):
    return tuple(u for u in self.units if u.is_present())

  def str_estimate(self):
    return sum([u.size for u in self.units], 0)
