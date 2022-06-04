import state
from collections import deque
import random

from narration import BattleNarrator
from battleview import TextBattleScreen
from pygameview import PGBattleScreen

from contexts import Context
from events import Event
import rps
import status
import battle_constants
import weather
# import state as s
import resources

class Battle():

  def __init__(self, army1, army2,
               debug_mode=False, automated=False, show_AI=False,
               view="PYGAME"):
    self.debug_mode = debug_mode
    self.state_stack = [state.GenesisState(self)]
    if view == "PYGAME":
      self.battlescreen = PGBattleScreen(self, 0, automated=automated,
                                           show_AI=show_AI)
    else:
      assert view == "TEXT"
      self.battlescreen = TextBattleScreen(self, 0, automated=automated,
                                       show_AI=show_AI)
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
    self.automated = automated # happening with no player actor (so we can suppress input, etc.) 
    self.imaginary = False # happening as part of an AI's mind in simulation
    self.show_AI = show_AI
    if view == "PYGAME":
      self.battlescreen.new()

  def close(self):
    self.queues = []
    for a in self.armies:
      a.unhook()
    self.armies = []
    self.narrator = None
    self.battlescreen = None
    
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

  def _init_day(self):
    """
    Cleans state, but also most importantly, makes it renderable.
    """
    # common knowledge: later take out
    self.date += 1
    self.weather = weather.random_weather()
    self.yomi_winner_id = -1
    self.yomis = None
    # setup stuff
    for i in [0, 1]:
      self.armies[i].yomi_edge = None
      # self.armies[i].bet_morale_change = 0
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
    formation_turn = FormationTurn(self, 0)
    formation_turn.enter_state()      

  def _draw_and_scout(self):
    ids = [0, 1]
    drawn_cards = [None, None]
    scouted_cards = [None, None]
    for i in ids:
      drawn_cards[i] = self.armies[i].tableau.draw_cards()
      scouted_cards[i] = self.armies[i].tableau.scouted_by(self.armies[1-i])
    return (drawn_cards, scouted_cards)
  
  # def _get_formations(self):
  #   drawn_cards, scouted_cards = self._draw_and_scout()
  #   Event(self, "scout_completed", Context({})).activate(drawn_cards, scouted_cards)
  #   for i in [0, 1]:
  #     self.armies[i].formation = self.armies[i].intelligence.get_formation(self)
  #   Event(self, "formation_completed", Context({})).activate()

  
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
    for i in [1, 0]:
      # originally these were in lists; the problem is you can change these lists, so make copies
      for unit in tuple(self.armies[i].units):
        for sta in tuple(unit.unit_status):
          ctxt = Context({"ctarget":unit})
          ss = sta.stat_str
          func_list = status.status_info(ss, func_key)
          if func_list: # found a function (func_name, kwargs)
            # convert arguments into context
            event_name = func_list[0]
            additional_opt = {"stat_str":ss}
            additional_opt.update(func_list[1]) # additional arguments
            Event(self, event_name, ctxt.copy(additional_opt)).activate()

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

  def _run_queue(self, queue_name):
    while self.queues[queue_name]:
      event, args = self.queues[queue_name].pop()
      event.activate(*args)

  def start_formations(self):
    drawn_cards, scouted_cards = self._draw_and_scout()
    Event(self, "scout_completed", Context({})).activate(drawn_cards, scouted_cards)
    formation_turn = FormationTurn(self, 0)
    formation_turn.enter_state()

  def start_orders(self):
    drawn_cards, scouted_cards = self._draw_and_scout()
    Event(self, "scout_completed", Context({})).activate(drawn_cards, scouted_cards)
    order_turn = OrderTurn(self, 0)
    order_turn.enter_state()
      
  def resolve_orders(self):
    """
    The battle logic that happens after logic is selected.
    Is public because AI also uses it to run mental simulations
    """
    resolution = Resolution(self)
    resolution.enter_state()
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
    Event(self, "turn_end", {"game_end":game_end}).activate()
    return game_end

      # def take_turn(self):
  #   """
  #   The main function which takes one turn of this battle.
  #   returns whether the battle is over
  #   """
  #   # formations
  #   self._init_day()
  #   self._get_formations()
  #   self._get_orders()
  #   return self.resolve_orders()
  # # exposed methods
  
  def start_battle(self):
    self._init_day()    
  # def start_battle(self):
  #   while(True):
  #     game_ended = self.take_turn()
  #     if game_ended:
  #       state = self.end_state()
  #       self.close()
  #       return state  

###############
# State Stuff #
###############

class FormationTurn(state.State):  
  def __init__(self, game, battle, armyid):
    super().__init__(game)
    self.battle = battle
    self.army = battle.armies[armyid]
    self.armyid = armyid
    self.battle.armies[armyid].intelligence.await_formation()

  def update(self, actions):
    if self.army.formation:
      if self.armyid == 0:
        self.exit_state()
        formation_turn = FormationTurn(self.game, self.battle, 1)
        formation_turn.enter_state()
      else:
        assert self.armyid == 1
        self.exit_state()
        Event(self.battle, "formation_completed", Context({})).activate()
        self.battle.start_orders()
    else:
      assert self.army.intelligence_type == 'PLAYER'
      if any(actions.values()):
        for k in actions:
          if actions[k]:
            self.army.formation = rps.FormationOrder(k)

class OrderTurn(state.State):
  def __init__(self, battle, armyid):
    super().__init__(battle)
    self.army = battle.armies[armyid]
    self.armyid = armyid
    self.controller.armies[armyid].intelligence.await_final()

  def update(self, actions):
    if self.army.order:
      if self.armyid == 0:
        self.exit_state()
        order_turn = OrderTurn(self.controller, 1)
        order_turn.enter_state()
      else:
        assert self.armyid == 1
        self.exit_state()
        Event(self.controller, "order_completed", Context({})).activate()
        self.controller.start_resolution()
    else:
      assert self.army.intelligence_type == 'PLAYER'
      if any(actions.values()):
        for k in actions:
          if actions[k]:
            self.army.order = rps.FinalOrder(k)

class Resolution(state.State):
  def __init__(self, battle):
    super().__init__(battle)
    self.controller.resolve_orders()

  def update(self, actions):
    if any(actions.values()):
      # update on any key
      self.controller._init_day()
  # TODO: IMPLEMENT THESE
        
  # def _get_orders(self):
  #   for i in [0, 1]:
  #     self.armies[i].order = self.armies[i].intelligence.get_final(self)

      
  # def _get_formations(self):
  #   for i in [0, 1]:
  #     self.armies[i].formation = self.armies[i].intelligence.get_formation(self)
  #   Event(self, "formation_completed", Context({})).activate()
