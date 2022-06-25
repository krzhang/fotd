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

import input_controller
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

  
class PGBattleView:
  """ a Pygame View + Controller for a battle object """

  def __init__(self, battle, armyid, automated=False, show_AI=False):
    self.game_width, self.game_height = WIDTH, HEIGHT
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" % (50, 50)

    self.screen = pygame.display.set_mode((self.game_width, self.game_height))
    pygame.display.set_caption(TITLE)

    self.input_controller = input_controller.InputController(self)
    
    self.running = True
    self.playing = True
    self.fps = FPS

    self.clock = pygame.time.Clock()
    
    pygame.font.init()
    pygame.mixer.init()

    self.battle = battle

    self.armyid = armyid
    
    self.infobox = InfoBox(self)
    self.console = Console(self)
    self.huddlebox = Huddle(self, "huddle",
                            header=text_convert("{ctarget_army}'s strategy session",
                                                templates={'ctarget_army':self.army}))
    self.manueverbox = Huddle(self, "manuevers",
                              header="Manuever recap")
    self.statebox = StateBox(self)
    self.narrator = BattleNarrator(self.battle, self)

    self.view_elements = [self.infobox,
                          self.console,
                          self.huddlebox,
                          self.manueverbox,
                          self.statebox,
                          self.narrator]

    self.view_stack = [self.console]
    
    self.debug_mode = self.battle.debug_mode
    self.automated = automated
    self.show_AI = show_AI

    self.actions = None 
    self.all_sprites = pygame.sprite.Group()
    
  @property
  def state_stack(self):
    return self.battle.state_stack

  def top_state(self):
    return self.state_stack[-1]
  
  def _top_action_receiver(self):
    """
    This is used to decide which thing receives the actions. It's a bit hackish right now.

    First, we look at the overlays; they take precedence and need to be flushed before the things
    on bottom activate.    
    """
    if self.manueverbox.buf:
      return self.manueverbox
    elif self.huddlebox.buf:
      return self.huddlebox
    elif self.console.buf:
      return self.console
    ts = self.top_state()
    # if isinstance(ts, state.Pause):
    #   return ts
    return ts

  def pause(self, pauser=None, pause_str=None):
    pause = state.Pause(self.battle, pauser=pauser, pause_str=pause_str)
    pause.enter_state()
  
  @property
  def army(self):
    return self.battle.armies[self.armyid]

  def new(self):
    self.background = Static(self, 0, 0, resources.IMAGE_PATH / "old-paper-800-600.jpg")
    armies = self.battle.armies
    facing = "SOUTH"
    for j in range(2):
      v_offset = 210+120*j
      army = armies[j]
      if j == 1:
        facing = "NORTH"
      for i, unit in enumerate(army.units):
        h_offset = 90 + 170*i
        spr = UnitSpr(self, h_offset, v_offset, resources.SPRITES_PATH / "Soldier.png", unit, facing)
    self.run()

  def input_events(self):
    """ 
    we turn input events (keyboard, mouse, etc.) into a digestible [actions] dictionary
    which then is handled by the state machine
    """
    self.actions = self.input_controller.events()
    
    # this code should go to the input_controller

  def update(self):
    self.all_sprites.update()
    dt = self.clock.tick()
    self.input_controller.update(dt)

    # decide which thing receives the actions

    ve = self._top_action_receiver()
    ve.update(self.actions)
    
  def draw(self, pause_str=None):
    if self.automated:
      return

    if self.playing:

      self.screen.fill(PColors.BLACK)

      # sprites
      self.all_sprites.draw(self.screen)

      # infobox
      self.infobox.mouseover = None
      for spr in self.all_sprites:
        if spr.infobox and spr.rect.collidepoint(pygame.mouse.get_pos()):
          self.infobox.mouseover = spr.mouseover_info()
          break

      # refactor later by going through view_elements
      self.infobox.render()
      self.console.render()
      self.statebox.render()
      if self.huddlebox.buf:
        self.huddlebox.render()
      elif self.manueverbox.buf:
        self.manueverbox.render()

      pygame.display.flip()

  def run(self):
    while self.playing:
      # self.clock.tick(self.fps)
      self.input_events()
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
        self.console.buf.append(converted_text)
      elif m == "huddle":
        self.huddlebox.buf.append(converted_text)
      elif m == 'order_phase':
        self.manueverbox.buf.append(converted_text)
      else:
        assert m == 'AI'
        if self.show_AI:
          self.console.console_buf.append(converted_text)
