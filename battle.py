import textutils
from textutils import Colors, yprint, pause, yprint_hrule
import random
import events
import numpy as np
import skills
import status
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
    self.morale_diff = 0
    self.gq = deque()
    self.date = 0
    self.order_history = []
    self.init_triggers()
    
  def init_triggers(self):
    self.triggers = {} # DOES NOTHIGN RIGHT NOW
    pass


  
  def gen_AI_order(self):
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
    
  def display_state(self):
    yprint_hrule()
    yprint("Weather: %s" % str(self.weather))
    for i in [0,1]:
      # yprint("Army %d:" % i)
      for u in self.armies[i].live_units():
        charstr = "{} {}".format(repr(u), " ".join((repr(s) for s in u.character.skills)))
        yprint(charstr)
        healthbar = textutils.disp_bar(20, u.size_base, u.size)
        yprint("  {} {} (SP: {}) {}".format(healthbar, u.size_repr(), u.speed, u.status_real_repr()))
      if i == 0:
        yprint("                                     VS")    
    yprint_hrule()
    return

  def init_turn_state(self):
    self.date += 1
    self.weather = Weather(random.choice(list(WEATHER)))

  def _run_status_handlers(self, func_key):
    for i in [0,1]:
      # originally these are in lists; the problem is you can change these lists, so make copies
      for unit in tuple(self.armies[i].live_units()):
        for sta in tuple(unit.unit_status):
          ctxt = events.Context(self, opt={"target":unit})
          sta.run_status_func(func_key, ctxt)

  def is_raining(self):
    return self.weather.text == "raining"

  def is_hot(self):
    return self.weather.text == "hot"

  def take_turn(self, orders):
    self.init_turn(orders)
    # preloading events
    yprint_hrule()
    yprint("Resolving Events: %s(%s) vs %s(%s)" % (self.order_history[-1][0],
                                                  self.armies[0].name,
                                                  self.order_history[-1][1],
                                                  self.armies[1].name))
    yprint_hrule()
    self._run_status_handlers("bot")
    while len(self.gq) > 0:
      event = self.gq.pop()
      event.activate()
      if event.event_type == "army_destroyed":
        return
    yprint("===========================================================")
    self._run_status_handlers("eot")
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
        event = events.Event(o2e[order], events.Context(self, opt={"target":u}))
        orderlist.append((speed, event))
    orderlist.sort(key=lambda x: x[0])
    for o in orderlist:
      self.gq.append(o[1])
      
