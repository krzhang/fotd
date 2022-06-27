# State Machine controller. Meant to be agnostic of the view.
import pygame as pg
import sys

class State():
  def __init__(self, battle): # a battle is a controller
    self.battle = battle
    self.prev_state = None
    self.phase = None

  def render(self, surface):
    pass

  def __str__(self):
    return ""

  def __repr__(self):
    return str(self)
  
  def enter_state(self):
    # print ("entered state " + str(self) + "({})".format(self.battle))
    if len(self.battle.state_stack) > 1:
      self.prev_state = self.battle.state_stack[-1]
    self.battle.state_stack.append(self)
    # print ("  state stack: {}".format(self.battle.state_stack))

  def exit_state(self):
    # print ("  state stack: {}".format(self.battle.state_stack))
    self.battle.state_stack.pop()
    # print ("exited state " + str(self) + "({})".format(self.battle))
    # print ("  state stack: {}".format(self.battle.state_stack))
    
  def update(self, actions):
    pass

class GenesisState(State):

  def __str__(self):
    return "Genesis State"
  
class Pause(State):
  def __init__(self, battle, pauser=None, pause_str=""):
    """ the [pauser] is the view (Console, main view, etc.) that generated the pause. """
    super().__init__(battle)
    pg.event.clear()
    self.pauser = pauser
    self.pause_str = pause_str
    self.phase = self.battle.state_stack[-1].phase
    
  def __str__(self):
    return "Paused"

  def update(self, actions):
    if actions and any(actions.values()):
      print("unpaused")
      self.exit_state()
      if self.pauser:
        self.pauser.update(actions)
