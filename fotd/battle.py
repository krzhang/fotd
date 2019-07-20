
from collections import deque
import random

from narration import BattleNarrator
import textutils
from battleview import BattleScreen
import contexts
import events
import rps
import skills
import status
import tableau
import battle_constants
import weather

class Battle():

  def __init__(self, army1, army2, debug_mode=False, automated=False):
    self.debug_mode = debug_mode
    self.battlescreen = BattleScreen(self, 0, automated=automated)
    self.narrator = BattleNarrator(self, self.battlescreen)
    self.armies = [army1, army2]
    for a in self.armies:
      a.hook(self)
    # 5 queues
    self.queues = {}
    for qname in battle_constants.QUEUE_NAMES:
      self.queues[qname] = deque()
    # other stuff
    self.date = 0
    self.weather = None
    self.yomis = None
    self.yomi_winner_id = -1
    self.yomi_list = []
    self.imaginary = False

  def close(self):
    self.queues = []
    for a in self.armies:
      a.unhook()
    self.armies = []
    self.narrator = None
    self.battlescreen = None
    
  def imaginary_copy(self):
    """
    creates an imaginary battle, used for mid-battle strategizing
    """
    bat = Battle(self.armies[0].copy(),
                  self.armies[1].copy(),
                  debug_mode=False,
                  automated=True)
    bat.date = self.date
    bat.weather = self.weather
    bat.yomis = self.yomis
    bat.yomi_winner_id = self.yomi_winner_id
    bat.yomi_list = self.yomi_list
    bat.imaginary = True
    return bat
  
  def end_state(self):
    wins = [False, False]
    for i in [0,1]:
      if self.armies[i].is_present():
        wins[i] = True
    return tuple(wins)
  
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
    self.queues[queue_name].appendleft(events.Event(self, event_type, context))

  def is_raining(self):
    return self.weather.text == "raining"

  def is_hot(self):
    return self.weather.text == "hot"

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
      # TODO: this is only helpful for view, so let view handle it
      self.armies[i].last_turn_morale = self.armies[i].morale
      self.armies[i].tableau.clear()
      for u in self.armies[i].present_units():
        u.attacked = []
        u.attacked_by = []
        u.targetting = None
        # TODO: same here
        u.last_turn_size = u.size
  
  def _get_formations_and_orders(self):
    ids = [0, 1]
    for i in ids:
      self.armies[i].tableau.draw_cards()
      self.armies[i].tableau.scouted_by(self.armies[1-i])
    for i in ids:
      self.armies[i].formation = self.armies[i].intelligence.get_formation(self)
    self.narrator.narrate_formations()

    # orders
    for i in ids:
      self.armies[i].tableau.draw_cards()
      self.armies[i].tableau.scouted_by(self.armies[1-i])
    for i in ids:
      # this is currently bad if player is second-player, because you can see the output
      # of the AI orders
      self.armies[i].order = self.armies[i].intelligence.get_final(self)

  def _handle_yomi(self):
    for i in [0, 1]:
      formation = self.formations[i]
      cost = rps.formation_info(str(formation), "morale_cost")[str(self.armies[i].order)]
      if cost:
        self.armies[i].bet_morale_change = cost
      else:
        self.armies[i].commitment_bonus = True

    self.yomi_winner_id = rps.orders_to_winning_armyid(self.orders) # -1 if None
    self.yomis = (rps.beats(self.orders[0], self.orders[1]),
                  rps.beats(self.orders[1], self.orders[0]))
    self.yomi_list.append(self.yomis)
    self.narrator.narrate_orders(self.yomi_winner_id)

  def _run_status_handlers(self, func_key):
    for i in [1, 0]:
      # originally these were in lists; the problem is you can change these lists, so make copies
      for unit in tuple(self.armies[i].units):
        for sta in tuple(unit.unit_status):
          ctxt = contexts.Context({"ctarget":unit})
          ss = sta.stat_str
          func_list = status.status_info(ss, func_key)
          if func_list: # found a function (func_name, kwargs)
            # convert arguments into context
            event_name = func_list[0]
            additional_opt = {"stat_str":ss}
            additional_opt.update(func_list[1]) # additional arguments
            events.Event(self, event_name, ctxt.copy(additional_opt)).activate()  

  def _send_orders_to_armies(self):
    orders = self.orders
    orderlist = []
    for i in [0, 1]:
      order = orders[i]
      bet = self.armies[i].bet_morale_change
      if bet:
        orderlist.append((0, "order_change",
                          contexts.Context({"ctarget_army":self.armies[i],
                                            "morale_bet":bet})))
      if self.yomi_winner_id == i:
        orderlist.append((0, "order_yomi_win",
                          contexts.Context({"ctarget_army":self.armies[i]})))
      for u in self.armies[i].present_units():
        speed = u.speed + random.uniform(-3, 3)
        if order == 'D':
          speed += 2.7
        orderlist.append((speed, "order_received",
                          contexts.Context(opt={"ctarget":u,
                                                "order":order})))
    orderlist.sort(key=lambda x: x[0])
    for o in tuple(orderlist):
      self.place_event(o[1], o[2], 'Q_ORDER')

  def _run_queue(self, queue_name):
    while self.queues[queue_name]:
      event = self.queues[queue_name].pop()
      event.activate()

  def resolve_orders(self):
    """
    The battle logic that happens after logic is selected.
    Is public because AI also uses it to run mental simulations
    """
    self._handle_yomi()
    # preloading events
    self._run_status_handlers("bot") # should be queue later
    self._send_orders_to_armies()
    self._run_queue('Q_ORDER')
    for i in [0, 1]:
      for u in self.armies[i].present_units():
        assert u.targetting
    self._run_queue('Q_MANUEVER')
    self._run_queue('Q_RESOLVE')
    self._run_status_handlers("eot") # should be queue later
    game_end = False
    for i in [0, 1]:
      if not self.armies[i].is_present():
        game_end = True
    events.Event(self, "turn_end", {"game_end":game_end}).activate()
    return game_end
    
  def take_turn(self):
    """
    The main function which takes one turn of this battle.
    returns whether the battle is over
    """
    # formations
    self._init_day()
    self._get_formations_and_orders()
    return self.resolve_orders()
  # exposed methods
  
  def start_battle(self):
    while(True):
      game_ended = self.take_turn()
      if game_ended:
        state = self.end_state()
        self.close()
        return state
