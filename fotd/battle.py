
from collections import deque
import random

from narration import BattleNarrator
import textutils
import contexts
import events
import rps
import skills
import status
import tableau
import battle_constants
import positions
import weather

class Battle():

  def __init__(self, army1, army2, debug_mode=False, automated=False):
    self.debug_mode = debug_mode
    self.battlescreen = textutils.BattleScreen(self, 0, automated=automated)
    self.narrator = BattleNarrator(self, self.battlescreen)
    self.armies = [army1, army2]
    for a in self.armies:
      a.battle = self
      a.tableau = tableau.Tableau(self, a)
      for u in a.units:
        for s in u.character.skills:
          u.add_unit_status(s.skill_str)
          # crazy bug here because add_unit_status will just run the constructor to
          # blah_STATUS without the associatied string, creating a status that's not from a
          # skillstring
          # u.unit_status.append(status.Status.FromSkillName(s.skill_str))
      a.commander.add_unit_status("is_commander")
    self.hqs = [positions.Position(self, self.armies[i].commander, i) for i in [0, 1]]
    self.dynamic_positions = []
    self.morale_diff = 0
    # 5 queues
    self.queues = {}
    for qname in battle_constants.QUEUE_NAMES:
      self.queues[qname] = deque()
    # other stuff
    self.order_history = []
    self.date = 0
    self.weather = None
    self.yomis = None
    self.yomi_winner = -1
    self.yomi_list = []

  @property
  def formations(self):
    return (self.armies[0].formation, self.armies[1].formation)
    
  @property
  def orders(self):
    return (self.armies[0].order, self.armies[1].order)
    
  def place_event(self, event_type, context, queue_name):
    """
    used when we want to make a new event on a queue of our choice 
    we pop from right, so we should place left.
    """
    self.queues[queue_name].appendleft(events.Event(event_type, context))

  def is_raining(self):
    return self.weather.text == "raining"

  def is_hot(self):
    return self.weather.text == "hot"

  def make_position(self, ctarget):
    newpos = positions.Position(self, ctarget) # meeting in the field
    self.dynamic_positions.append(newpos)
    return newpos

  ########################
  # Turn logic functions #
  ########################

  def _init_day(self):
    """
    Cleans state, but also most importantly, makes it renderable.
    """
    # common knowledge: later take out
    self.date += 1
    self.weather = weather.random_weather()
    self.yomi_winner = -1
    self.yomis = None
    # setup stuff
    for i in [0, 1]:
      self.armies[i].yomi_edge = None
      self.armies[i].bet_morale_change = 0
      self.armies[i].formation = None
      self.armies[i].order = None
      self.armies[i].formation_bonus = 1.0
      self.armies[i].commitment_bonus = False
      self.armies[i].last_turn_morale = self.armies[i].morale
      self.armies[i].tableau.clear()
      for u in self.armies[i].present_units():
        u.move(self.hqs[u.army.armyid])
        u.targetting = None
        u.last_turn_size = u.size
    assert all((p.is_empty() for p in self.dynamic_positions))
    self.dynamic_positions = []
  
  def _get_formations_and_orders(self):
    for i in [0, 1]:
      myarmy = self.armies[i]
      myarmy.tableau.draw_cards()
      myarmy.formation = myarmy.intelligence.get_formation(self, i)
    self.narrator.narrate_formations()

    # orders
    for i in [0, 1]:
      myarmy = self.armies[i]
      myarmy.tableau.draw_cards()
      myarmy.order = myarmy.intelligence.get_final(self, i)
 
  def _run_status_handlers(self, func_key):
    for i in [0, 1]:
      # originally these were in lists; the problem is you can change these lists, so make copies
      for unit in tuple(self.armies[i].units):
        for sta in tuple(unit.unit_status):
          ctxt = contexts.Context(self, opt={"ctarget":unit})
          ss = sta.stat_str
          func_list = status.status_info(ss, func_key)
          if func_list: # found a function (func_name, kwargs)
            # convert arguments into context
            event_name = func_list[0]
            additional_opt = {"stat_str":ss}
            additional_opt.update(func_list[1]) # additional arguments
            events.Event(event_name, ctxt.copy(additional_opt=additional_opt)).activate()  

  def _send_orders_to_armies(self, orders):
    self.order_history.append(orders)
    self.yomi_winner = rps.orders_to_winning_army(orders) # -1 if None
    self.yomis = (rps.beats(orders[0], orders[1]), rps.beats(orders[1], orders[0]))
    self.yomi_list.append(self.yomis)
    orderlist = []
    for i in [0, 1]:
      order = orders[i]
      formation = self.formations[i]
      cost = rps.formation_info(str(formation), "morale_cost")[str(order)]
      if cost:
        orderlist.append((0, "order_change",
                          contexts.Context(self, opt={"ctarget_army":self.armies[i],
                                                      "morale_bet":cost})))
      else:
        self.armies[i].commitment_bonus = True
      if self.yomi_winner == i:
        orderlist.append((0, "order_yomi_win",
                          contexts.Context(self, opt={"ctarget_army":self.armies[i]})))
      for u in self.armies[i].present_units():
        u.attacked = []
        u.attacked_by = []
        u.targetting = None
        speed = u.speed + random.randint(-3, 3)
        if order == 'D':
          speed += 7
        orderlist.append((speed, "order_received",
                          contexts.Context(self, opt={"ctarget":u,
                                                      "order":order})))
    orderlist.sort(key=lambda x: x[0])
    for o in orderlist:
      self.place_event(o[1], o[2], 'Q_ORDER')

  def _run_queue(self, queue_name):
    while self.queues[queue_name]:
      event = self.queues[queue_name].pop()
      event.activate()
      if any((not self.armies[i].is_present()) for i in [0, 1]):
        # TODO: replace with arbitary leave condition
        return
      
  def take_turn(self):
    """
    The main function which takes one turn of this battle.
    """
    # formations
    self._init_day()
    self._get_formations_and_orders()
    # preloading events
    self._run_status_handlers("bot") # should be queue later
    self._send_orders_to_armies(self.orders)
    self._run_queue('Q_ORDER')
    for i in [0,1]:
      for u in self.armies[i].present_units():
        assert u.targetting
    self._run_queue('Q_MANUEVER')
    self._run_queue('Q_RESOLVE')
    self._run_status_handlers("eot") # should be queue later

  def losing_status(self):
    losing = [False, False] # they can theoretically both lose
    for i in [0, 1]:
      if not self.armies[i].is_present():
        self.battlescreen.yprint("{}'s units have all been defeated.".format(
          textutils.disp_army(self.armies[i])))
        losing[i] = True
      if self.armies[i].morale <= 0:
        losing[i] = True
        self.battlescreen.yprint("{} collapses due to catastrophic morale.".format(
          textutils.disp_army(self.armies[i])))
    return tuple(losing)
