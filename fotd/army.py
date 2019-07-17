import status
import intelligence
import rps

class Unit(object):
  def __init__(self, character, size, speed):
    self.character = character
    self.name = character.name
    self.size_base = size
    self.size = size
    self.speed = speed
    self.army = None
    self.color = None
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
    return self.color_str()

  def color_str(self):
    return "$[{}]${}$[7]$".format(self.color, self.name)
  
  def set_color(self, color):
    self.color = color
    self.character.color = color

  @property
  def skills(self):
    return self.character.skills

  def __str__(self):
    return str(self.character)

  def has_unit_status(self, stat_str):
    return stat_str in [s.stat_str for s in self.unit_status]

  def add_unit_status(self, stat_str):
    """ as strings. DON'T USE WITH SKILLS """
    if not self.has_unit_status(stat_str):
      self.unit_status.append(status.Status(stat_str))

  def get_order(self):
    return self.army.order

  def move(self, newpos):
    if self.position:
      # could come here from None
      self.position.remove_unit(self)
    newpos.add_unit(self)
    self.position = newpos

  def leave_battle(self):
    if self.position:
      # could come here from None
      self.position.remove_unit(self)
    self.position = None

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
    val = 1.0 # generically this is a 1/5 hit chance, so a full sized unit does about 3 damage
    # val = rps.formation_info(self.army.formation, "physical_offense")
    # val *= float(self.size)/4.0
    val *= self._generic_multiplier()
    return float(val)

  def physical_defense(self):
    val = 9.0
    if self.is_defended():
      val *= 1.5
    val *= self._generic_multiplier()
    return float(val)

  def arrow_offense(self):
    val = 1.0 
    # val = rps.formation_info(self.army.formation, "arrow_offense")
    val *= self._generic_multiplier()
    return val

  def arrow_defense(self):
    val = 19.0 
    # val = rps.formation_info(self.army.formation, "arrow_defense")
    val *= self._generic_multiplier()
    return val

  def is_defended(self):
    return self.has_unit_status("defended")

  def is_present(self):
    return self.size > 0 and self.character.health > 0

class Army(object):
  def __init__(self, name, units, armyid, color, intelligence_type, morale):
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
    self.intelligence = intelligence.INTELLIGENCE_FROM_TYPE[intelligence_type]()
    self.morale = morale
    self.last_turn_morale = morale
    # things to be linked later
    self.turn_status = {} # status for each turn; yomi edge, formation bonus, etc.
    self.yomi_edge = None # used in battles to see if RPS was won
    self.battle = None
    self.formation_bonus = 1.0
    self.formation = None
    self.order = None
    self.commitment_bonus = False
    
  def __repr__(self):
    return self.color_str()

  def color_str(self):
    return "$[{}]${}$[7]$".format(self.color, self.name)
  
  def get_order(self):
    return self.order

  def get_yomi_count(self):
    ind = self.battle.date-1
    chain = 0
    while self.battle.yomi_list[ind][self.armyid] == 1:
      ind -= 1
      chain += 1
      if ind == -1:
        break
    return chain
  
  def is_present(self):
    return any([u for u in self.units if u.is_present()])

  def present_units(self):
    return tuple(u for u in self.units if u.is_present())

  def str_estimate(self):
    return sum([u.size for u in self.units], 0)
