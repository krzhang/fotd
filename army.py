import skills
import status
import intelligence
import colors
from textutils import disp_unit

class Unit(object):
  def __init__(self, character, size, speed):
    self.character = character
    self.name = character.name
    self.size_base = size
    self.size = size
    self.speed = speed
    self.army = None
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
    return disp_unit(self)

  def set_color(self, color):
    self.color = color
    self.character.color = color

  def __str__(self):
    return str(self.character)
  
  def has_unit_status(self, stat_str):
    return stat_str in [s.stat_str for s in self.unit_status]
  
  def add_unit_status(self, stat_str):
    """ as strings. DON'T USE WITH SKILLS """
    if not self.has_unit_status(stat_str):
      self.unit_status.append(status.Status(stat_str))

  def move(self, newpos):
    if self.position:
      # could come here from None
      self.position.remove_unit(self)
    newpos.add_unit(self)
    self.position = newpos
      
  def remove_unit_status(self, statstr):
    #import pdb; pdb.set_trace()
    #self.unit_status = [s for s in self.unit_status if s.stat_str != statstr]
    self.unit_status.remove(status.Status(statstr))

  def _generic_multiplier(self):
    val = 1.0
    if self.has_unit_status("trymode_activated"):
      val *= 1.5
    if self.has_unit_status("burned"):
      val /= 1.5
    return val
  
  def physical_offense(self):
    val = rps.get_formation_bonus(self.army.formation, "physical_offense")
    val *= float(self.size)/3.5
    val *= self._generic_multiplier()
    return float(dam)

  def physical_defense(self):
    val = rps.get_formation_bonus(self.army.formation, "physical_defense")
    val *= float(self.size)/3.5
    val *= 1.5 # geeric defense bonus
    if self.is_defended():
      val *= 1.5
    val *= self._generic_multiplier()
    return float(dam)
  
  def arrow_offense(self):
    val = rps.get_formation_bonus(self.army.formation, "arrow_offense")
    val *= 2.0
    val *= self._generic_multiplier()
    return val

  def arrow_defense(self):
    val = rps.get_formation_bonus(self.army.formation, "arrow_defense")
    val *= 18.0
    val *= self._generic_multiplier()
    return val
  
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
      u.army = self
      u.set_color(color)
    self.intelligence_type = intelligence_type
    self.intelligence = intelligence.INTELLIGENCE_FROM_TYPE[intelligence_type]
    self.turn_status = {} # status for each turn; yomi edge, formation bonus, etc.
    self.yomi_edge = None # used in battles to see if RPS was won
    self.morale = 10
    self.battle = None
    self.formation_bonus = 1.0
    self.formation = None
    self.order = None
    
  def __repr__(self):
    return "Army({})".format(self.name)

  def is_present(self):
    return any([u for u in self.units if u.is_present()])

  def present_units(self):
    return tuple(u for u in self.units if u.is_present())

  def str_estimate(self):
    return sum([u.size for u in self.units], 0)
