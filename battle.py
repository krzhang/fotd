import textutils
from textutils import Colors, yprint, pause, yprint_hrule
import random
import events
import numpy as np
import skills
import status
import positions
from collections import deque
from mathutils import normalize
import utils

PLAYER_ARMY = 0
AI_ARMY = 1

WEATHER = {
  "sunny": {
    "transitions": {
      
    },
    "viz": Colors.GREEN + "Sunny" + Colors.ENDC
  },
  "hot": {
    "viz": Colors.RED+ "HOT" + Colors.ENDC    
  },
  "raining": {
    "blocks": [],
    "viz": Colors.BLUE + "Raining" + Colors.ENDC
  }
}

class Weather(object):
  def __init__(self, text):
    self.text = text

  def __str__(self):
    return WEATHER[self.text]["viz"]

class Battle(object):

  QUEUE_NAMES = ["Q_PRELIM", "Q_ORDER", "Q_MANUEVER", "Q_RESOLVE", "Q_CLEANUP"]
  
  def __init__(self, army1, army2):
    self.armies = [army1, army2]
    for a in self.armies:
      for u in a.units:
        for s in u.character.skills:
          u.add_unit_status(s.skill_str)
          # crazy bug here because add_unit_status will just run the constructor to
          # blah_STATUS without the associatied string, creating a status that's not from a
          # skillstring
          # u.unit_status.append(status.Status.FromSkillName(s.skill_str))
      a.commander.add_unit_status("is_commander")
    self.hqs = [positions.Position(self, self.armies[i].commander, i) for i in [0,1]]
        
    self.dynamic_positions = []
    self.morale_diff = 0
    # 5 queues
    self.queues = {}
    for qname in Battle.QUEUE_NAMES:
      self.queues[qname] = deque()
    # other stuff
    self.date = 0
    self.order_history = []
    self.init_battle_state()

  def init_battle_state(self):
    self.date += 1
    self.weather = Weather(random.choice(list(WEATHER)))
    for i in [0,1]:
      for u in self.armies[i].units:
        u.position = self.hqs[i]
        self.hqs[i].add_unit(u)
    
  def place_event(self, event_type, context, queue_name):
    """ used when we want to make a new event on a queue of our choice """
    self.queues[queue_name].append(events.Event(event_type, context))
    
  def display_state(self):
    yprint_hrule()
    yprint("Day {} {}".format(self.date, str(self.weather)))
    textutils.yprint_hrule()
    for p in self.hqs:
      p.display()
      if p.hqid == 0:
        yprint("                                               VS")
    yprint_hrule()
    return

  def get_player_order(self):
    while(True):
      self.display_state()
      order = textutils.yinput("Input orders (A/D/I):")
      if self.legal_order(order):
        return order.upper()
      else:
        yprint("Illegal order.")        
      
  def get_AI_order(self):
    # 2 paths: RPS and story-driven soul reading
    parmy = self.armies[PLAYER_ARMY].live_units()
    priors = np.array([10,10,10])
    for unit in parmy:
      for sk in unit.character.skills:
        skstr = sk.skill_str
        if skstr in skills.SKILLS:
          priors += np.array(skills.SKILLS[skstr]["ai_eval"])
    # adjusting for size
          # import pdb; pdb.set_trace()
    priors += np.array([1,0,0])*(self.armies[PLAYER_ARMY].str_estimate() -
                self.armies[AI_ARMY].str_estimate())
    # TODO: adjusting for battlefield conditions
    m = min(priors)
    if m < 0:
      priors += np.array([1-m, 1-m, 1-m])
      assert min(priors) > 0
    newpriors = normalize(priors)
    yprint("  AI predicts player (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*newpriors))
    counters = np.array(list(newpriors[2:]) + list(newpriors[:2]))
    yprint("  AI counterpicks    (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*counters))
    return np.random.choice(["A", "D", "I"], p=counters)    

  def _run_status_handlers(self, func_key):
    for i in [0,1]:
      # originally these are in lists; the problem is you can change these lists, so make copies
      for unit in tuple(self.armies[i].units):
        for sta in tuple(unit.unit_status):
          ctxt = events.Context(self, opt={"ctarget":unit})
          sta.run_status_func(func_key, ctxt)

  def is_raining(self):
    return self.weather.text == "raining"

  def is_hot(self):
    return self.weather.text == "hot"

  def _run_queue(self, queue_name):
    while len(self.queues[queue_name]) > 0:
      event = self.queues[queue_name].pop()
      event.activate()
      if any((not self.armies[i].is_alive()) for i in [0,1]):
        # TODO: replace with arbitary leave condition
        return
      
  def make_position(self, ctarget):
    newpos = positions.Position(self, ctarget) # meeting in the field
    self.dynamic_positions.append(newpos)
    return newpos

  def display_positions(self):
    for p in self.hqs + self.dynamic_positions:
      if not p.is_empty():
        p.display(debug=True)
    
  def take_turn(self, orders):
    self.init_turn(orders)
    # preloading events
    yprint_hrule()
    yprint("Day Starts: %s (%s) vs %s (%s)" % (self.order_history[-1][0],
                                                  self.armies[0].name,
                                                  self.order_history[-1][1],
                                                  self.armies[1].name))
    yprint_hrule()
    self._run_status_handlers("bot") # should be queue later
    yprint_hrule(debug=True)
    yprint("Running Orders;", debug=True)
    yprint_hrule(debug=True)
    self._run_queue('Q_ORDER')
    pause()
    yprint_hrule(debug=True)
    yprint("Units Manuever;", debug=True)
    yprint_hrule(debug=True)
    self._run_queue('Q_MANUEVER')
    yprint_hrule(debug=True)
    yprint_hrule(debug=True)
    yprint("All Units in Position;",debug=True)
    yprint_hrule(debug=True)
    self.display_positions()
    #pause()
    yprint_hrule(debug=True)
    yprint("Fighting Resolves",debug=True)
    yprint_hrule(debug=True)
    self._run_queue('Q_RESOLVE')    
    self._run_status_handlers("eot") # should be queue later
    for i in [0,1]:
      for u in self.armies[i].units:
        if u.position:
          u.move(self.hqs[u.armyid])
    assert all((p.is_empty() for p in self.dynamic_positions))
    self.dynamic_positions = []
    pause(clear=True)
    
  def legal_order(self, order):
    return order.upper() in ["A", "D", "I"]
  
  def win_army(self):
    for i in [0, 1]:
      if not self.armies[i].is_alive():
        return 1-i
    return None
    
  def init_turn(self, orders):
    o2e = {"A": "attack_order", "D": "defense_order", "I":"indirect_order"}
    self.order_history.append(orders)
    orderlist = []
    for i in [0, 1]:
      order = orders[i]
      for u in self.armies[i].live_units():
        u.attacked = []
        u.attacked_by = []
        u.targetting = None
        speed = u.speed
        speed += random.choice([-3,-2,-1,0,1,2,3])
        if order == 'D':
          speed += 7
        orderlist.append((speed, o2e[order], events.Context(self, opt={"ctarget":u})))
    orderlist.sort(key=lambda x: x[0])
    for o in orderlist:
      self.place_event(o[1], o[2], "Q_ORDER")
      
