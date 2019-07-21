import status
import intelligence
import rps
import tableau

class Unit(object):
  def __init__(self, character, size, speed):
    self.character = character
    self.size_base = size
    self.size = size
    self.speed = speed
    self.army = None
    self.color = None
    self.unit_status = [] # not to be confused with character-status
    self.targetting = None
    self.attacked = [] # enemies attacked in a turn
    self.attacked_by = []
    self.last_turn_size = None
    self.present_state = 'PRESENT'

  def __eq__(self, other):
    return hasattr(self, "character") and hasattr(other, "character") and self.character == other.character

  def __repr__(self):
    return self.color_name()

  def unhook(self):
    self.army = None
    self.character = None
    
  def copy(self):
    newunit = Unit(self.character.copy(), self.size, self.speed)
    newunit.present_state = self.present_state
    newunit.attacked = self.attacked.copy()
    newunit.attacked_by = self.attacked_by.copy()
    return newunit

  def is_commander(self):
    return self.has_unit_status("is_commander")
  
  def color_name(self):
    return "$[{}]${}$[7]$".format(self.color, self.name)

  def str_unit_size(unit):
    csize = colors.color_size(unit.size, unit.size_base) + str(unit.size) + "$[7]$"
    return "{}/{}".format(str(csize), str(unit.size_base))
  
  def str_targetting(self):
    """ 
    dispays targetting status (a tuple of (action, target)) for a unit that's created by then
    unit's (final) order.
    ex: 'sneaking towards X' 
    """
    if not self.targetting: # set to none etc.
      return "doing nothing"
    if self.targetting[0] == "marching":
      return "marching -> " + self.targetting[1].color_name()
    if self.targetting[0] == "defending":
      return "staying put"
    assert self.targetting[0] == "sneaking"
    return "sneaking -> " + self.targetting[1].color_name()

  def set_color(self, color):
    self.color = color
    self.character.color = color

  @property

  def name(self):
    return self.character.name
  
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

  def leave_battle(self, state):
    self.present_state = state

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
    return self.present_state == 'PRESENT'

class Army(object):
  def __init__(self, name, units, armyid, color, intelligence_type, morale):
    self.name = name
    self.units = units
    self.commander = self.units[0]
    self.commander.add_unit_status("is_commander")
    self.color = color
    self.armyid = armyid
    for u in units:
      u.army = self
      u.set_color(color)
      for s in u.character.skills:
        u.add_unit_status(s.skill_str)
          # crazy bug here because add_unit_status will just run the constructor to
          # blah_STATUS without the associatied string, creating a status that's not from a
          # skillstring
          # u.unit_status.append(status.Status.FromSkillName(s.skill_str))
    self.intelligence = intelligence.INTELLIGENCE_FROM_TYPE[intelligence_type](self)
    self.morale = morale
    self.last_turn_morale = morale
    # things to be linked later
    self.yomi_edge = None # used in battles to see if RPS was won
    self.battle = None
    self.formation_bonus = 1.0
    self.formation = None
    self.order = None
    self.commitment_bonus = False
    self.battle_lost = False
    self.tableau = tableau.Tableau(self)
    self.bet_morale_change = 0
    
  def __repr__(self):
    return self.color_name()

  def copy(self, intelligence_type):
    tarmy = Army(self.name + "_copy",
                  [u.copy() for u in self.present_units()],
                  self.armyid,
                  self.color,
                  intelligence_type,
                  self.morale)
    tarmy.yomi_edge = self.yomi_edge
    tarmy.formation_bonus = self.formation_bonus
    tarmy.formation = self.formation
    tarmy.order = self.order
    tarmy.commitment_bonus = self.commitment_bonus
    tarmy.battle_lost = self.battle_lost
    tarmy.tableau = self.tableau.copy(tarmy)
    tarmy.bet_morale_change = self.bet_morale_change
    # need to also run things from battle.init_day; messy
    return tarmy

  def find_unit(self, unit):
    """
    NOT an eq check; this is to find a unit by name without being hte same unit (so we can 
    transfer information given an imaginary copy of the army)
    """
    for u in self.units:
      if u.character.name == unit.character.name:
        return u
    assert False
    
  def other_army(self):
    return self.battle.armies[1-self.armyid]
  
  def hook(self, battle):
    self.battle = battle

  def unhook(self):
    self.tableau.unhook()
    self.tableau = None
    self.battle = None
    for u in self.units:
      u.unhook()
    
  def color_name(self):
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
    # what about commanders? currently relying on morale to take care of everything...
    return any(self.present_units())

  def present_units(self):
    return tuple(u for u in self.units if u.is_present())

  def state_viewed_by(self, army):
    """
    returns a view that the other army can use for AI purposes
    """
    return None
