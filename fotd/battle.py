# Controller object for Battle

import state
from collections import deque
import random

from narration import BattleNarrator
from battleview import MockBattleView
from pygameview import PGBattleView

from contexts import Context
from events import Event
import rps
import status
import settings_battle
import weather
# import state as s

class Battle():
  """ An abstract battle that doesn't understand views"""
  def __init__(self, army1, army2,
               debug_mode=False, automated=False, show_AI=False):
    self.debug_mode = debug_mode
    self.state_stack = [state.GenesisState(self)]

    self.view = MockBattleView(self, 0, automated=automated, show_AI = show_AI) # to be hooked later

    self.armies = [army1, army2]
    for a in self.armies:
      a.hook(self)
    # 5 queues
    self.queues = {}
    for qname in settings_battle.QUEUE_NAMES:
      self.queues[qname] = deque()
    # other stuff
    self.date = 0
    self.weather = None
    self.yomis = None
    self.yomi_winner_id = -1
    self.yomi_list = []
    self.automated = automated # happening with no player actor (so we can suppress input, etc.) 
    self.imaginary = False # happening as part of an AI's mind in simulation
    self.show_AI = show_AI
    self.playing = False
    self.result = None # eventually tuple of (player 1 win, player 2 win)
    
  def __str__(self):
    my_str = ""
    if self.automated:
      my_str += "automated,"
    if self.imaginary:
      my_str += "imaginary"
    return my_str

  def close(self):
    self.queues = []
    for a in self.armies:
      a.unhook()
    self.armies = []
    self.narrator = None
    self.view = None
    
  def imaginary_copy(self, intelligence_type):
    """
    creates an imaginary battle, used for mid-battle strategizing
    """
    bat = Battle(self.armies[0].copy(intelligence_type),
                  self.armies[1].copy(intelligence_type),
                  debug_mode=False,
                  automated=True, show_AI=self.show_AI)
    bat.date = self.date
    
    bat.weather = self.weather
    bat.yomis = self.yomis
    bat.yomi_winner_id = self.yomi_winner_id
    # WARNING: forgetting the copy() causes a heisenbug...
    bat.yomi_list = self.yomi_list.copy()
    bat.automated = True
    bat.imaginary = True
    return bat
    
  @property
  def formations(self):
    return (self.armies[0].formation, self.armies[1].formation)
    
  @property
  def orders(self):
    return (self.armies[0].order, self.armies[1].order)
    
  # def place_event(self, event_type, context, queue_name, args=[]):
  #   self.queues[queue_name].appendleft((Event(self, event_type, context),
  #                                       args))

  def is_raining(self):
    return self.weather.text == "raining"

  def is_hot(self):
    return self.weather.text == "hot"

  ########################
  # Turn logic functions #
  ########################

  def _draw_and_scout(self, phase):
    ids = [0, 1]
    drawn_cards = [None, None]
    scouted_cards = [None, None]
    for i in ids:
      drawn_cards[i] = self.armies[i].tableau.draw_cards(phase)
      scouted_cards[i] = self.armies[i].tableau.scouted_by(self.armies[1-i], phase)
    return (drawn_cards, scouted_cards)
  
  def _handle_yomi(self):
    for i in [0, 1]:
      formation = self.formations[i]
      cost = rps.formation_info(str(formation), "morale_cost")[str(self.armies[i].order)]
      if cost:
        # self.armies[i].bet_morale_change = cost
        self.armies[i].commitment_bonus = False
        Event(self, "order_change",
              Context({"ctarget_army":self.armies[i], "morale_cost":cost})).activate()
      else:
        # self.armies[i].bet_morale_change = 0
        self.armies[i].commitment_bonus = True

    self.yomi_winner_id = rps.orders_to_winning_armyid(self.orders) # -1 if None
    self.yomis = (rps.beats(self.orders[0], self.orders[1]),
                  rps.beats(self.orders[1], self.orders[0]))
    self.yomi_list.append(self.yomis)
    if self.yomi_winner_id in [0, 1]:
      Event(self, "order_yomi_win", Context({})).activate(self.armies[self.yomi_winner_id])
    Event(self, "order_yomi_completed", Context({})).activate(self.yomi_winner_id)

  def _run_status_handlers(self, func_key):
    if func_key == "bot":
      queue_name = "Q_PRELIM"
    else:
      assert func_key == "eot"
      queue_name = "Q_CLEANUP"
    for i in [1, 0]:
      # originally these were in lists; the problem is you can change these lists, so make copies
      for unit in tuple(self.armies[i].units):
        for sta in tuple(unit.unit_status):
          ctxt = Context({"ctarget":unit})
          ss = sta.stat_str
          func_list = getattr(sta, func_key)
          if func_list: # found a function (func_name, kwargs)
            # convert arguments into context
            event_name = func_list[0]
            additional_opt = {"stat_str":ss}
            additional_opt.update(func_list[1]) # additional arguments
            Event(self, event_name, ctxt.copy(additional_opt)).defer(queue_name)

  def _send_orders_to_armies(self):
    orders = self.orders
    orderlist = []
    for i in [0, 1]:
      order = orders[i]
      for u in self.armies[i].present_units():
        speed = u.speed + random.uniform(-3, 3)
        if order == 'D':
          speed += 2.7
        orderlist.append((speed, "order_received", Context(opt={"ctarget":u, "order":order})))
    orderlist.sort(key=lambda x: x[0])
    for o in tuple(orderlist):
      Event(self, o[1], o[2]).defer('Q_ORDER')

  # def _run_queue(self, queue_name):
  #   while self.queues[queue_name]:
  #     event, args = self.queues[queue_name].pop()
  #     event.activate(*args)

  def pop_queue(self, queue_name):
    if self.queues[queue_name]:
      event, args = self.queues[queue_name].pop()
      event.activate(*args)
      return True
    return False
  
  def start_battle(self):
    print("Let's start the battle!")
    self.playing = True
    InitDay(self).enter_state()

  def end_battle(self):
    self.playing = False
    wins = [False, False]
    for i in [0,1]:
      if self.armies[i].is_present():
        wins[i] = True
    self.result = tuple(wins)
    
  def update(self, actions):
    state = self.state_stack[-1]
    state.update(actions)

###############
# State Stuff #
###############

  # def resolve_orders(self):
  #   """
  #   The battle logic that happens after logic is selected.
  #   Is public because AI also uses it to run mental simulations
  #   """
  #   Resolution(self).enter_state()
  #   self._handle_yomi()
  #   # preloading events
  #   self._run_status_handlers("bot") # should be queue later
  #   self._send_orders_to_armies()
  #   self._run_queue('Q_ORDER')
  #   for i in [0, 1]:
  #     for u in self.armies[i].present_units():
  #       assert u.targetting
  #   self._run_queue('Q_MANUEVER')
  #   self._run_queue('Q_RESOLVE')
  #   self._run_status_handlers("eot") # should be queue later
  #   game_end = False
  #   for i in [0, 1]:
  #     if not self.armies[i].is_present():
  #       game_end = True
  #   Event(self, "turn_end", {"game_end":game_end}).activate()
  #   return game_end

  
class InitDay(state.State):
  """ Cleans the slate, checks for win conditions, etc. """
  def __init__(self, battle):
    super().__init__(battle)

  def update(self, actions):
    self.battle.date += 1
    self.battle.weather = weather.random_weather()
    self.battle.yomi_winner_id = -1
    self.battle.yomis = None
    # setup stuff
    for i in [0, 1]:
      army = self.battle.armies[i]
      army.yomi_edge = None
      # army.bet_morale_change = 0
      army.formation = None
      army.order = None
      army.formation_bonus = 1.0
      army.commitment_bonus = False
      # TODO: this is only helpful for view, so let view handle it
      army.last_turn_morale = army.morale
      army.tableau.clear()
      for u in army.present_units():
        u.attacked = []
        u.attacked_by = []
        u.targetting = None
        # TODO: same here
        u.last_turn_size = u.size
    print("Day initialized")
    self.exit_state()
    FormationTurn(self.battle, 0).enter_state() # this kicks off the state machine

  def __str__(self):
    return "Initializing day {}".format(self.battle.date)

class FormationTurn(state.State):  
  def __init__(self, battle, armyid):
    super().__init__(battle)
    self.army = battle.armies[armyid]
    self.armyid = armyid

    drawn_cards, scouted_cards = self.battle._draw_and_scout("formations")
    Event(self.battle, "scout_completed", Context({})).activate(drawn_cards, scouted_cards)
    
    self.battle.armies[armyid].intelligence.await_formation(self.battle)
    self.phase = "formation"

  def __str__(self):
    return "Waiting for formations from {}".format(self.armyid)
 
  def update(self, actions):
    if self.army.formation:
      if self.armyid == 0:
        print("Got formation " + str(self.army.formation) + " for " + str(self.armyid))
        self.armyid = 1
        self.army = self.battle.armies[self.armyid]
        self.army.intelligence.await_formation(self.battle)
      else:
        assert self.armyid == 1
        self.exit_state()
        Event(self.battle, "formation_completed", Context({})).activate()
        print("Got formation " + str(self.army.formation) + " for " + str(self.armyid))
        
        OrderTurn(self.battle, 0).enter_state()
    else:
      if self.army.intelligence_type == 'PLAYER':
        if actions and any(actions.values()):
          for k in actions:
            if k in ["A", "D", "I"] and actions[k]:
              self.army.formation = rps.FormationOrder(k)
      else:
        pass
        # if it's AI, its probably taking its turn right now; just let it wait.

            
class OrderTurn(state.State):
  def __init__(self, battle, armyid):
    super().__init__(battle)
    self.army = battle.armies[armyid]
    self.armyid = armyid

    drawn_cards, scouted_cards = self.battle._draw_and_scout("orders")
    Event(self.battle, "scout_completed", Context({})).activate(drawn_cards, scouted_cards)
    
    self.battle.armies[armyid].intelligence.await_final(self.battle)
    self.phase = "order"
    
  def __str__(self):
    return "Waiting for orders from {}".format(self.armyid)

  def update(self, actions):
    if self.army.order:
      if self.armyid == 0:
        self.armyid = 1
        self.army = self.battle.armies[self.armyid]
        self.army.intelligence.await_final(self.battle)
      else:
        assert self.armyid == 1
        self.exit_state()
        Event(self.battle, "order_completed", Context({})).activate()
        print("Got orders " + str(self.army.order) + " for " + str(self.armyid))
        
        Resolution(self.battle).enter_state()
    else:
      if self.army.intelligence_type == 'PLAYER':
        if actions and any(actions.values()):
          for k in actions:
            if k in ["A", "D", "I"] and actions[k]:
              self.army.order = rps.FinalOrder(k)
      else:
        pass
        # if it's AI, its probably taking its turn right now; just let it wait.


class Resolution(state.State):
  """ abstract resolution class that resolves through queues. """

  def __init__(self, battle):
    super().__init__(battle)
    self.phase = "resolution"
    self.subphase_index = 0
    # in settings_battle, we have different queues corresponding to different
    # subphases. QUEUE_NAMES = ["Q_PRELIM", "Q_ORDER", "Q_MANUEVER", "Q_RESOLVE", "Q_CLEANUP"]
    self.queue_names = settings_battle.QUEUE_NAMES.copy()
    self.battle._handle_yomi()
    self.battle._run_status_handlers("bot")

  def __str__(self):
    return "Resolution - subphase {}".format(self.subphase_index)

  def update(self, actions):
    task_performed = self.battle.pop_queue(self.queue_names[0])
    if task_performed:
      return
    else: # queue is idling
      self.queue_names = self.queue_names[1:]
      if not self.queue_names:
        game_end = False
        for i in [0, 1]:
          if (not self.battle.armies[i].is_present()) or self.battle.imaginary:
            # we exit for 2 reasons:
            # 1. someone lost TODO: can activate this earlier
            # 2. this is an imaginary battle and we have finished the turn
            self.exit_state()
            self.battle.end_battle()
            return
        Event(self.battle, "turn_end", {"game_end":game_end}).activate()
        self.exit_state()
        InitDay(self.battle).enter_state()
        return
      cur_queue = self.queue_names[0]
      if cur_queue == "Q_PRELIM": # prelims 
        self.battle._handle_yomi()
        self.battle._run_status_handlers("bot")
      elif cur_queue == "Q_ORDER": # orders
        self.battle._send_orders_to_armies()
      elif cur_queue == "Q_MANUEVER": # manuevers
        pass
      elif cur_queue == "Q_CLEANUP": # cleanup          
        self.battle._run_status_handlers("eot")       
