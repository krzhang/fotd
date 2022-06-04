# State Machine controller. Meant to be agnostic of the view.
import pygame

class State():
  def __init__(self, controller): # a battle is a controller
    self.controller = controller
    self.prev_state = None

  def update(self, action):
    pass

  def render(self, surface):
    pass

  def enter_state(self):
    if len(self.controller.state_stack) > 1:
      self.prev_state = self.controller.state_stack[-1]
    self.controller.state_stack.append(self)

  def exit_state(self):
    self.controller.state_stack.pop()

  def update(self, actions):
    pass

class GenesisState(State):
  pass
  
class EndState(State):
  pass
  
class QuitState(State):

  def update(self, actions):
    pg.quit()
    sys.exit()
  
class UserInput(State):

  def __init__(self, controller, callback):
    super().__init__(controller)
    self.callback = callback
    
  def update(self, actions):
    if actions['Q']:
      quitting = QuitState(self.controller)
      quitting.enter_state()
    elif any(actions.values()):
      for k in actions:
        if actions[k]:
          self.exit_state()
          callback(k)
      
