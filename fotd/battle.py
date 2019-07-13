
from collections import deque
import random

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
    self.battlescreen = textutils.BattleScreen(self, 0, automated=automated)
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
    self.debug_mode = debug_mode
    self.date = 0
    self.weather = None
    self.formations = None
    self.orders = None
    self.yomis = None
    self.yomi_winner = -1
    self.yomi_list = []
    self.init_day()

  def init_day(self):
    """
    Cleans state, but also most importantly, makes it renderable.
    """
    # common knowledge: later take out
    self.date += 1
    self.weather = weather.random_weather()
    self.formations = None
    self.orders = None
    self.yomi_winner = -1
    self.yomis = None
    # setup stuff
    for i in [0, 1]:
      self.armies[i].yomi_edge = None
      self.armies[i].bet_morale_change = 0
      self.armies[i].formation = None
      self.armies[i].order = None
      self.armies[i].formation_bonus = 1.0
      self.armies[i].last_turn_morale = self.armies[i].morale
      self.armies[i].tableau.clear()
      for u in self.armies[i].present_units():
        u.move(self.hqs[u.army.armyid])
        u.ctargetting = None
        u.last_turn_size = u.size
    assert all((p.is_empty() for p in self.dynamic_positions))
    self.dynamic_positions = []

  # observer pattern?
  # def make_speech(self, unit, speech):
  #   self.battlescreen.disp_speech(unit, speech)

  # def make_skill_narration(self, skill_str, other_str, success=None):
  #   self.battlescreen.disp_skill_narration(skill_str, other_str, success)

  # def make_duel(self, csource, ctarget, loser_history, health_history, damage_history):
  #   self.battlescreen.disp_duel(csource, ctarget, loser_history, health_history, damage_history)

  def place_event(self, event_type, context, queue_name):
    """
    used when we want to make a new event on a queue of our choice 
    we pop from right, so we should place left.
    """
    self.queues[queue_name].appendleft(events.Event(event_type, context))

  # def yprint(self, text, templates={}, debug=False):
  #   self.battlescreen.yprint(text, templates, debug)

  def _run_status_handlers(self, func_key):
    for i in [0, 1]:
      # originally these were in lists; the problem is you can change these lists, so make copies
      for unit in tuple(self.armies[i].units):
        for sta in tuple(unit.unit_status):
          ctxt = contexts.Context(self, opt={"ctarget":unit})
          ss = sta.stat_str
          func_list = status.status_info(ss, func_key)
          if func_list: # found a function (func_name, kwargs)
            event_name = func_list[0]
            additional_opt = {"status":ss}
            additional_opt.update(func_list[1])
            events.Event(event_name, ctxt.copy(additional_opt=additional_opt)).activate()

  def is_raining(self):
    return self.weather.text == "raining"

  def is_hot(self):
    return self.weather.text == "hot"

  def _run_queue(self, queue_name):
    while self.queues[queue_name]:
      event = self.queues[queue_name].pop()
      event.activate()
      if any((not self.armies[i].is_present()) for i in [0, 1]):
        # TODO: replace with arbitary leave condition
        return

  def make_position(self, ctarget):
    newpos = positions.Position(self, ctarget) # meeting in the field
    self.dynamic_positions.append(newpos)
    return newpos

  def get_formations(self):
    orders = [None, None]
    for i in [0, 1]:
      self.armies[i].tableau.draw_cards()
      orders[i] = self.armies[i].intelligence.get_formation(self, i)
      self.armies[i].formation = orders[i]
    return tuple(orders)

  def get_orders(self):
    orders = [None, None]
    for i in [0, 1]:
      self.armies[i].tableau.draw_cards()
      orders[i] = self.armies[i].intelligence.get_order(self, i)
      self.armies[i].order = orders[i]
    return tuple(orders)

  def _initiate_orders(self, orders):
    self.order_history.append(orders)
    self.yomi_winner = rps.orders_to_winning_army(orders) # -1 if None
    self.yomis = (rps.beats(orders[0], orders[1]), rps.beats(orders[1], orders[0]))
    self.yomi_list.append(self.yomis)
    self.battlescreen.yprint("Winner: {}".format(self.yomi_winner), debug=True)
    self.battlescreen.yprint("Yomis: {}".format(self.yomis), debug=True)
    orderlist = []
    for i in [0, 1]:
      order = orders[i]
      formation = self.formations[i]
      cost = rps.formation_info(formation, "morale_cost")[order]
      if cost:
        orderlist.append((0, "order_change", contexts.Context(self, opt={"ctarget_army":self.armies[i], "morale_bet":cost})))
      if self.yomi_winner == i:
        orderlist.append((0, "order_yomi_win", contexts.Context(self, opt={"ctarget_army":self.armies[i]})))
      for u in self.armies[i].present_units():
        u.attacked = []
        u.attacked_by = []
        u.targetting = None
        speed = u.speed
        speed += random.choice([-3,-2,-1,0,1,2,3])
        if order == 'D':
          speed += 7
        orderlist.append((speed, rps.order_to_event(order),
                          contexts.Context(self, opt={"ctarget":u})))
    orderlist.sort(key=lambda x: x[0])
    for o in orderlist:
      self.place_event(o[1], o[2], "Q_ORDER")

  def take_turn(self):
    self.formations = self.get_formations()
    for i in [0,1]:
      form = self.formations[i]
      self.battlescreen.yprint("{} takes a {}.".format(self.armies[i],
                                          rps.formation_info(form, "desc")))
    self.orders = self.get_orders()
    self._initiate_orders(self.orders)
    # preloading events
    self._run_status_handlers("bot") # should be queue later
    self._run_queue('Q_ORDER')
    self._run_queue('Q_MANUEVER')
    self._run_queue('Q_RESOLVE')
    self._run_status_handlers("eot") # should be queue later
    # self.battlescreen.pause_and_display() # could have undisplayed stuff
    self.init_day()

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
