from settings_pygame import *
import pygame
import sys

class InputController(object):
  def __init__(self, view):
    self.view = view # typically the battlescreen
    self.cooldown = 0
    
  def disable(self):
    """ disable the input; used to not queue up commands and to add pauses """
    pygame.event.clear()
    self.cooldown = INPUT_COOLDOWN_WINDOW
    
  def is_enabled(self):
    return (self.cooldown == 0)

  def events(self):
    actions = {"A": False,
               "D": False,
               "I": False,
               "Q": False,
               "KEYPRESSED": False}    

    if not self.is_enabled():
      return
    
    for event in pygame.event.get():

      # key detection
      if event.type == pygame.KEYDOWN:
        kr = pygame.key.name(event.key)
        kn = kr.upper()
        print(kn)
        actions["KEYPRESSED"] = True
        if kn in actions:
          if kn == 'Q':
            pygame.quit()
            sys.exit(0)
          # pt = pygame.time.get_ticks()
          actions[kn] = True
        self.disable()
        break
    return actions
  
  def update(self, time_taken):
    self.cooldown = max(self.cooldown - time_taken, 0)
