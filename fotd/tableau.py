"""
Information related to the skillcards. Each army in a battle has a tableau, and they
form the 'card game' part of the battle.
"""

import random

import rps
import skills

class TableauCard(object):
  """
  a Skillcard in the context of a Tableau (an actual battle, so it belongs to some unit)
  as opposed to a platonic skillcard

  self.visibility[armyid] gives information about what armyid knows about this card for
  this round. It can be:

  1. False (not drawn and thus not seen)
  2. [phase]: possible values are "formation", "order", "resolution"
     [phase] describes when the card was drawn/detected. 

  Example: {0:"formation" 1: "order"} means army 1 found it during formation (probably by 
  drawing) and army 2 found it during order phase (probably by scouting). This means during
  formation phase collection army 2 would see a card but they wouldn't know which
  """
  def __init__(self, sc, unit):
    self.skillcard = sc
    self.unit = unit
    self.armyid = unit.army.armyid

    self.visibility = {0:False, 1:False}

    
  def copy(self, unit):
    # this is important for e.g. creating an imaginary card for a different unit
    return TableauCard(self.skillcard, unit)

  def __hash__(self):
    return hash((self.skillcard, self.unit.id, self.armyid))

  def __eq__(self, other):
    return hash(self) == hash(other)
  
  def str_seen_by_army(self, army):
    if self.visible_to(army):
      return "<{}{}:{}$[7]$>".format(rps.order_info(self.skillcard.order, "color_bulbed"),
                                     self.skillcard.order,
                                     self.skillcard.skill)
    else:
      return "<$[7,3]$?:??????$[7]$>"

  def clear(self):
    self.visibility = {0:False, 1:False}
    
  def visible_to(self, army):
    """ Currently, if it's not False, then it's visible."""
    return bool(self.visibility[army.armyid])

  def make_visible_to(self, army, phase):
    self.visibility[army.armyid] = phase

  def make_visible_to_all(self, phase="resolution"):
    for army in self.unit.army.battle.armies:
      self.make_visible_to(army, phase)
    
  def activates_on(self):
    return self.skillcard.order

  def activates_against(self):
    # todo: change to more flexible later
    return [rps.BEATS[str(self.skillcard.order)]]

class Tableau():
  """
  The 'card game' part of the battle state: skillcards, skillcards, hands, etc. and visibility
  each side has a tableau
  """
  def __init__(self, army):
    self.army = army
    self.decks = {u:[] for u in self.army.units}
    # for each user, a list of cards

    for u in self.army.units:
      for s in u.skills:
        for sc in s.possible_skillcards():
          self.decks[u].append(TableauCard(sc, u))

  def unhook(self):
    self.army = None
    
  def copy(self, newarmy):
    """
    make a copy with a different perspective armyid
    """
    newtab = Tableau(newarmy)
    for u in self.army.units:
      u_new = newarmy.find_unit(u)
      newtab.decks[u_new] = []
      for tc in self.decks[u]:
        sc = tc.skillcard
        tc_new = TableauCard(sc, u_new)
        for i in [0, 1]:
          tc_new.visibility[i] = tc.visibility[i]
        newtab.decks[u_new].append(tc_new)
    return newtab

  @property
  def battle(self):
    return self.army.battle

  @property
  def armyid(self):
    return self.army.armyid

  def clear(self):
    """
    Wipes state; kills everything except deck. used when we clear state before a turn.
    """
    for u in self.army.units:
      for tc in self.decks[u]:
        tc.clear()
        
  def draw_cards(self, phase):
    """
    draw hands from the deck of skillcards. 
    Done twice: 
    1. at beginning of turn, before collecting formations
    2. after collecting formations, before collecting orders
    """
    new_cards = []
    for u in self.army.units: # maybe present_units??
      for tc in self.decks[u]:
        if tc.visibility[self.armyid] == False: # not yet drawn
          sc = tc.skillcard
          proc_chance = sc.bulb[str(sc.order)]
          if ((random.random() < proc_chance) and
              (self.battle.weather.text not in sc.illegal_weather)):
            # a new legal card is drawn
            tc.visibility[self.armyid] = phase
            tc.make_visible_to(self.army, phase)
            new_cards.append(tc)
    return new_cards
  
  def scouted_by(self, army, phase):
    """
    the other army scouts this tableau, and can see some of the new cards
    """
    scouted_cards = []
    assert army.armyid == 1-self.armyid
    for u in self.army.units: # maybe present_units??
      for tc in self.decks[u]:
        if tc.visible_to(self.army) and not tc.visible_to(army):
          if random.random() < 0.5:
            # scouting is 50% right now. This can improve later
            tc.make_visible_to(army, phase)
            scouted_cards.append(tc)
    return scouted_cards

  # def visible_skillcard(self, viewer_army, unit, skillcard_str, order):
  #   """
  #   Mostly for the view: can [viewer_army] see the activation for [skillcard] for
  #   a particular [order]?
  #   """
  #   for sc in self.visible_bulbed_cards(viewer_army):
  #     if (sc.sc_str == skillcard_str and
  #         sc.unit == unit and
  #         sc.order == order):
  #       return True
  #   return False
  
  # def visible_bulbed_cards(self, viewer_army):
  #   visible_dict = {}
  #   for key in self.sc_dict:
  #     if self.sc_dict[key]: # has to be prepped
  #       if key.visible_to(viewer_army):
  #         visible_dict[key] = True
  #   return visible_dict

  # def get_unit_cards(self, unit):
  #   """ 
  #   returns {"active": [], "inactive": []}, where each item is a list of skillcards.
  #   """
  #   # inactive means skills that are not bulbed
  #   inactive_skillist = [s.str_fancy(success=False)
  #                        for s in unit.character.skills if
  #                        not bool(s.activation) == 'passive']
  #   inactive_skillstr = " ".join(inactive_skillist)
  #   # 'passive' means skills that are used and are not bulbed, meaning they *are* active
  #   active_skillist = [disp_text_activation(('*:' + s.short()),
  #                                             success=None, upper=False)
  #                      for s in unit.character.skills if
  #                      bool(s.activation) == 'passive']
  #   active_skillcards = [sc.str_seen_by_army(self.army) for sc in unit.army.tableau.bulbed_by(unit)]
  #   if inactive_skillstr:
  #     sepstr = " | "
  #   else:
  #     sepstr = "| "
  #   active_skillstr = " ".join(active_skillist + active_skillcards)

  # def bulbed_cards(self):
  #   return [key for key in self.sc_dict if self.sc_dict]
  
  # def bulbed_by(self, unit):
  #   blist = []
  #   for key in self.sc_dict:
  #     if self.sc_dict[key]:
  #       if key.unit == unit:
  #         blist.append(key)
  #   return blist
