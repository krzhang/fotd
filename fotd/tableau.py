"""
Information related to the skillcards. Each army in a battle has a tableau, and they
form the 'card game' part of the battle.
"""

import random

import rps
import skills

class SkillCard():
  """
  a single skillcard that can be bulbed up.
  """
  def __init__(self, sc_str, unit, order):
    self.sc_str = sc_str
    self.skill = skills.Skill(skills.skillcard_info(sc_str, "skill"))
    self.unit = unit
    self.order = order
    self.armyid = unit.army.armyid
    self.visibility = {0:False, 1:False}

  def copy(self, unit):
    # this is important as we are creating an imaginary card for a different unit
    return SkillCard(self.sc_str, unit, self.order)

  def __hash__(self):
    return hash((self.sc_str, self.unit.name, str(self.order), self.armyid))

  def __eq__(self, other):
    return (self.sc_str, self.unit.name, str(self.order)) == (other.sc_str, other.unit.name, str(other.order))
  
  def str_seen_by_army(self, army):
    if self.visible_to(army):
      return "<{}{}:{}$[7]$>".format(rps.order_info(self.order, "color_bulbed"),
                                     self.order,
                                     self.skill.short())
    else:
      return "<$[7,3]$?:??????$[7]$>"
    
  def visible_to(self, army):
    return self.visibility[army.armyid]

  def make_visible_to(self, army):
    self.visibility[army.armyid] = True

  def make_visible_to_all(self):
    for army in self.unit.army.battle.armies:
      self.make_visible_to(army)
    
  def activates_on(self):
    return self.order

  def activates_against(self):
    # todo: change to more flexible later
    return [rps.BEATS[str(self.order)]]

def visible_list(hand, army):
  return [h for h in hand if h.visible_to(army)]

class Tableau():
  """
  The 'card game' part of the battle state: skillcards, skillcards, hands, etc. and visibility
  each side has a tableau
  """
  def __init__(self, army):
    self.army = army
    self.sc_dict = {}

  def unhook(self):
    self.army = None
    
  def copy(self, newarmy):
    """
    make a copy with a different perspective armyid
    """
    newtab = Tableau(newarmy)
    for key in self.sc_dict:
      newtab.sc_dict[key.copy(unit=newarmy.find_unit(key.unit))] = self.sc_dict[key]
    return newtab

  @property
  def battle(self):
    return self.army.battle

  @property
  def armyid(self):
    return self.army.armyid

  @property
  def bv(self):
    # remove later
    return self.battle.view
  
  def clear(self):
    """
    Wipes state; kills everything except deck. used when we clear state before a turn.
    """
    self.sc_dict = {}
    # self.stacks = {'A':[], 'D':[], 'I':[]}
    for un in self.army.present_units():
      for sk in un.skills:
        sc_str = skills.get_skillcard(sk)
        if sc_str:
          for order_str in ['A', 'D', 'I']:
            sc = SkillCard(sc_str, un, rps.FinalOrder(order_str))
            self.sc_dict[sc] = False # in our deck, not yet drawn
        # now the deck has all the possible skillcards

  def draw_cards(self):
    """
    draw hands from the deck of skillcards. Done twice: before the first formation call and once

    """
    new_cards = []
    for sc in self.sc_dict:
      if self.sc_dict[sc] == False: # not yet drawn
        proc_chance = skills.skillcard_info(sc.sc_str, "bulb")[str(sc.order)]
        if ((random.random() < proc_chance) and
            (self.battle.weather.text not in skills.skillcard_info(sc.sc_str, "illegal_weather"))):
          # a new legal card is drawn
          self.sc_dict[sc] = True
          sc.make_visible_to(self.army)
          new_cards.append(sc)
    return new_cards
  
  def scouted_by(self, army):
    """
    the other army scouts this tableau, and can see some of the new cards
    """
    scouted_cards = []
    assert army.armyid == 1-self.armyid
    for sc in self.sc_dict:
      if self.sc_dict[sc] and not sc.visible_to(army):
        if random.random() < 0.5:
          sc.make_visible_to(army)
          scouted_cards.append(sc)
    return scouted_cards

  def visible_bulbed_cards(self, viewer_army):
    visible_dict = {}
    for key in self.sc_dict:
      if self.sc_dict[key]: # has to be prepped
        if key.visible_to(viewer_army):
          visible_dict[key] = True
    return visible_dict

  def get_unit_cards(self, unit):
    """ 
    returns {"active": [], "inactive": []}, where each item is a list of skillcards.
    """
    # inactive means skills that are not bulbed
    inactive_skillist = [s.str_fancy(success=False)
                         for s in unit.character.skills if
                         not bool(skills.skill_info(s.skill_str, 'activation') == 'passive')]
    inactive_skillstr = " ".join(inactive_skillist)
    # 'passive' means skills that are used and are not bulbed, meaning they *are* active
    active_skillist = [disp_text_activation(('*:' + s.short()),
                                              success=None, upper=False)
                       for s in unit.character.skills if
                       bool(skills.skill_info(s.skill_str, 'activation') == 'passive')]
    active_skillcards = [sc.str_seen_by_army(self.army) for sc in unit.army.tableau.bulbed_by(unit)]
    if inactive_skillstr:
      sepstr = " | "
    else:
      sepstr = "| "
    active_skillstr = " ".join(active_skillist + active_skillcards)


    
  def bulbed_cards(self):
    return [key for key in self.sc_dict if self.sc_dict]
  
  def bulbed_by(self, unit):
    blist = []
    for key in self.sc_dict:
      if self.sc_dict[key]:
        if key.unit == unit:
          blist.append(key)
    return blist
