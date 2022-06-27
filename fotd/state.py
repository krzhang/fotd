# State Machine controller. Meant to be agnostic of the view.
import pygame as pg
import sys

class State():
  def __init__(self, battle): # a battle is a controller
    self.battle = battle
    self.prev_state = None
    self.phase = None

  def update(self, action):
    pass

  def render(self, surface):
    pass

  def __str__(self):
    return ""
  
  def enter_state(self):
    #print ("entered state " + str(self) + "({})".format(self.battle))
    if len(self.battle.state_stack) > 1:
      self.prev_state = self.battle.state_stack[-1]
    self.battle.state_stack.append(self)

  def exit_state(self):
    self.battle.state_stack.pop()
    #print ("exited state " + str(self) + "({})".format(self.battle))
    
  def update(self, actions):
    pass

class GenesisState(State):

  def __str__(self):
    return "Genesis State"
  
class EndState(State):
  pass
  
class QuitState(State):

  def update(self, actions):
    pg.quit()
    sys.exit()
  
# class UserInput(State):

#   def __init__(self, battle, callback):
#     super().__init__(battle)
#     self.callback = callback
    
#   def update(self, actions):
#     if actions['Q']:
#       quitting = QuitState(self.battle)
#       quitting.enter_state()
#     elif any(actions.values()):
#       for k in actions:
#         if actions[k]:
#           self.exit_state()
#           callback(k)

class Pause(State):
  def __init__(self, battle, pauser=None, pause_str=""):
    """ the [pauser] is the view (Console, main view, etc.) that generated the pause. """
    super().__init__(battle)
    pg.event.clear()
    self.pauser = pauser
    self.pause_str = pause_str
    self.phase = self.prev_state.phase
    
  def __str__(self):
    return "Paused"

  def update(self, actions):
    if actions and any(actions.values()):
      self.exit_state()
      if self.pauser:
        self.pauser.update(actions)
