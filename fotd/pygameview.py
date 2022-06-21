"""
pygame related abstractions. The main thing here is PGBattleView, which
is a kind of view and replaces the ASCII one in battleview.
"""
import logging
import sys
import os

import pygame

from settings_pygame import *
import resources

from colors import PColors, YCodes
from ytext import YText, disp_text_activation, disp_bar_custom

from templates import text_convert

import rps
import skills
import settings_battle
import state
from textbox import InfoBox, Huddle, Console, StateBox
from narration import BattleNarrator

# move to settings later

BASE_DIR = os.getcwd()
# RESOURCES_DIR = os.path.join(BASE_DIR, "Resources")
TITLE = "Battle"

from sprites import *

PAUSE_STRS = {
  # "MORE_STR": Colors.INVERT + "MORE... [hit a key]" + Colors.ENDC,
  # "FORMATION_ORDER": Colors.INVERT +  "Input $[4]$FORMATION" + Colors.INVERT + " for army {armyid}$[7]$",
  # "FINAL_ORDER": Colors.INVERT + "Input $[4]$ORDERS" + Colors.INVERT + " for army {armyid}$[7]$"
  "MORE_STR": "MORE... [hit a key]",
  "FORMATION_ORDER": "Input Formation",
  "FINAL_ORDER": "Input Orders"
}


class InputController(object):
  def __init__(self, view):
    self.view = view # typically the battlescreen
    self.cooldown = 0
    
  def disable(self):
    """ disable the input; used to not queue up commands and to add pauses """
    self.cooldown = INPUT_COOLDOWN_WINDOW
    
  def is_enabled(self):
    return (self.cooldown == 0)

  def update(self, time_taken):
    self.cooldown = max(self.cooldown - time_taken, 0)
  
class PGBattleView:
  """ a Pygame View + Controller for a battle object """

  def __init__(self, battle, armyid, automated=False, show_AI=False):
    self.game_width, self.game_height = WIDTH, HEIGHT
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" % (50, 50)

    self.screen = pygame.display.set_mode((self.game_width, self.game_height))
    pygame.display.set_caption(TITLE)

    self.input_controller = InputController(self)
    
    self.running = True
    self.playing = True
    self.fps = FPS

    self.clock = pygame.time.Clock()
    
    pygame.font.init()
    pygame.mixer.init()

    self.battle = battle
    
    self.infobox = InfoBox(self)
    self.console = Console(self)
    self.huddle = Huddle(self)
    self.statebox = StateBox(self)
    self.narrator = BattleNarrator(self.battle, self)
    
    # self.max_screen_len = 24
    # self.max_armies_len = 17
    # self.max_stat_len = 3
    # self.max_console_len = 3
    # self.max_footer_len = 1
    
    self.debug_mode = self.battle.debug_mode
    self.armyid = armyid
    # self.army = self.battle.armies[armyid]
    self.automated = automated
    self.show_AI = show_AI

    self.actions = {"A": False,
                    "D": False,
                    "I": False,
                    "Q": False}
    
    self.all_sprites = pygame.sprite.Group()
    
  @property
  def state_stack(self):
    return self.battle.state_stack

  def pause(self):
    pause = state.Pause(self.battle)
    pause.enter_state()
  
  @property
  def army(self):
    return self.battle.armies[self.armyid]

  # def _get_input(self, pause_str, accepted_inputs):
  #   pygame.event.clear()
  #   while True:
  #     event = pygame.event.wait()
  #     if event.type == pygame.QUIT:
  #       pygame.quit()
  #       sys.exit()
  #     elif event.type == pygame.KEYDOWN:
  #       kn = pygame.key.name(event.key)
  #       if kn.upper() in accepted_inputs:
  #         return kn.upper()

  # def pause_and_display(self, pause_str=None):
  #   if self.automated:
  #     return
  #   self.draw()
  #   pygame.event.clear()
  #   while True:
  #     event = pygame.event.wait()
  #     if event.type == pygame.KEYDOWN:
  #       return

  def new(self):
    self.background = Static(self, 0, 0, resources.IMAGE_PATH / "old-paper-800-600.jpg")
    armies = self.battle.armies
    facing = "SOUTH"
    for j in range(2):
      v_offset = 120+240*j
      army = armies[j]
      if j == 1:
        facing = "NORTH"
      for i, unit in enumerate(army.units):
        h_offset = 90 + 170*i
        spr = UnitSpr(self, h_offset, v_offset, resources.SPRITES_PATH / "Soldier.png", unit, facing)
    self.run()
    
  def events(self):

    # this code should go to the input_controller
    
    self.actions = {"A": False,
                    "D": False,
                    "I": False,
                    "Q": False}    

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.playing = False

      # key detection
      if event.type == pygame.KEYDOWN:
        kr = pygame.key.name(event.key)
        kn = kr.upper()
        print(kn)
        if kn in self.actions:
          if kn == 'Q':
            pygame.quit()
            sys.exit(0)
          pt = pygame.time.get_ticks()
          if self.input_controller.is_enabled():
            self.actions[kn] = True
            self.input_controller.disable()
            
  def update(self):
    self.all_sprites.update()
    self.state_stack[-1].update(self.actions)
    dt = self.clock.tick()
    self.input_controller.update(dt)
    
  def draw(self, pause_str=None):
    if self.automated:
      return

    if self.playing:

      # if self.huddle_buf:
      #   self._render_and_pause_huddle()
      # if self.order_buf:
      #   self._render_and_pause_order()

      self.screen.fill(PColors.BLACK)

      # sprites
      self.all_sprites.draw(self.screen)

      # infobox
      mouseover = None
      for spr in self.all_sprites:
        if spr.infobox and spr.rect.collidepoint(pygame.mouse.get_pos()):
          mouseover = spr.mouseover_info()
          break

      self.infobox.handle_info(mouseover)
      self.screen.blit(self.infobox.surface, (BG_WIDTH, 0))

      # console
      self.console.render()
      self.screen.blit(self.console.surface, (0, BG_HEIGHT))

      # state
      self.statebox.render()
      self.screen.blit(self.statebox.surface, (BG_WIDTH, BG_HEIGHT))

      # huddle
      if self.huddle.huddle_buf:
        print ("Got huddles!")
        self.huddle.render()
        self.screen.blit(self.huddle.surface, (BG_WIDTH/4, BG_HEIGHT/4))
        self.pause()
        
      pygame.display.flip()


  def run(self):
    while self.playing:
      # self.clock.tick(self.fps)
      self.events()
      self.update()
      self.draw()

  def disp_activated_narration(self, activated_text, other_str, success=None):
    """ 
    What to display when we want to make a narration involving a skill / skillcard
    (really any string)
    """
    if activated_text:
      preamble = disp_text_activation(activated_text, success) + " "
    else:
      preamble = ""
    if success:
      successtr = "SUCCESS!"
    else:
      successtr = "FAIL!"
    if not other_str:
      other_str = disp_text_activation(successtr, success)
    self.yprint(preamble + other_str)

  def disp_chara_speech(self, chara, speech, context):
    """
    What to display when a character says something.
    """
    self.yprint("{}: '$[2]${}$[7]$'".format(chara.color_name(), speech),
                templates=context)

  def disp_duel(self, csource, ctarget, loser_history, health_history, damage_history):
    duelists = [csource, ctarget]
    self.yprint("{csource} and {ctarget} face off!",
                templates={"csource":csource,
                           "ctarget":ctarget})
    i = len(health_history)-1
    bars = [None, None]
    for j in [0, 1]:
      last_health = health_history[i][j]
      bars[j] = disp_bar_custom([YCodes.CYAN, YCodes.RED, YCodes.GREY],
                                  ['=', '*', '.'],
                                  [last_health,
                                   0,
                                   20 - last_health])
    self.yprint("after {} bouts:   {} {} vs {} {}".format(i,
                                                          csource.color_name(),
                                                          bars[0],
                                                          bars[1],
                                                          ctarget.color_name()))

  def input_battle_order(self, order_type, armyid):
    """
    Input a list of orders. The orders are objects (probably rps.Order()) with 
    - colored_abbrev method for display
    - str method for input
    """
    if order_type == 'FORMATION_ORDER':
      order_list = [rps.FormationOrder(s) for s in rps.FORMATION_ORDER_LIST]
    else:
      assert order_type == 'FINAL_ORDER'
      order_list = [rps.FinalOrder(s) for s in rps.FINAL_ORDER_LIST]
    
    pausestr_1 = PAUSE_STRS[order_type].format(**{"armyid":armyid})
    render_list = [order.color_abbrev() for order in order_list]
    pausestr_2 = " ({}):$[7]$".format("/".join(render_list))
    return self._get_input(pausestr_1 + pausestr_2,
                           [str(order).upper() for order in order_list])

  ############
  # Printing #
  ############     
  def yprint(self, text, templates=None, debug=False, mode=("console",)):
    # the converting means to convert, based on the template, which converting function to use.
    # {ctarget} will always be converted to Unit for example
    if self.automated or text is None:
      return
    converted_text = text_convert(text, templates)
    if debug and not self.debug_mode:
      return
    # can assert we are not automated and there's text
    # so we get here if either SHOW_DEBUG or debug=False, which means we send it to the buffer
    for m in mode:
      if m == "console":
        self.console.console_buf.append(converted_text)
      elif m == "huddle":
        self.huddle.huddle_buf.append(converted_text)
      elif m == 'order_phase':
        pass
        # self.order_buf.append(converted_text)
      else:
        assert m == 'AI'
        if self.show_AI:
          self.huddle.huddle_buf.append(converted_text)
