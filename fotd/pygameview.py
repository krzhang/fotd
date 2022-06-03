"""
pygame related abstractions. The main thing here is PGBattleScreen, which
is a kind of view and replaces the ASCII one in battleview.
"""
import logging
import sys

import pygame as pg
import os
from colors import IColors as c
from colors import Colors

import rps

# move to settings later

BASE_DIR = os.getcwd()
# RESOURCES_DIR = os.path.join(BASE_DIR, "Resources")
VERSION = "0.2dev"

BG_WIDTH = 800
BG_HEIGHT = 600
INFO_WIDTH = 200 # info on the RHS
CONSOLE_HEIGHT = 200 # console buffer on the bottom

WIDTH = BG_WIDTH + INFO_WIDTH
HEIGHT = BG_HEIGHT + CONSOLE_HEIGHT
FPS = 30
TITLE = "Battle"

import resources
from sprites import *
from templates import CONVERT_TEMPLATES_DISPS, convert_templates

PAUSE_STRS = {
  "MORE_STR": Colors.INVERT + "MORE... [hit a key]" + Colors.ENDC,
  "FORMATION_ORDER": Colors.INVERT +  "Input $[4]$FORMATION" + Colors.INVERT + " for army {armyid}$[7]$",
  "FINAL_ORDER": Colors.INVERT + "Input $[4]$ORDERS" + Colors.INVERT + " for army {armyid}$[7]$" 
}

class PGBattleScreen:
  """ a Pygame battle object """

  def __init__(self, battle, armyid, automated=False, show_AI=False):
    self.game_width, self.game_height = WIDTH, HEIGHT
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" % (50, 50)

    self.screen = pg.display.set_mode((self.game_width, self.game_height))
    pg.display.set_caption(TITLE)

    # self.clock = pg.time.clock()
    self.running = True
    self.playing = True
    self.fps = FPS

    pg.font.init()
    pg.mixer.init()

    self.console_buf = []
    self.huddle_buf = []
    self.order_buf = []
    self.max_screen_len = 24
    self.max_armies_len = 17
    self.max_stat_len = 3
    self.max_console_len = 3
    self.max_footer_len = 1
    
    self.battle = battle
    self.debug_mode = self.battle.debug_mode
    self.armyid = armyid
    # self.army = self.battle.armies[armyid]
    self.automated = automated
    self.show_AI = show_AI

    self.all_sprites = pg.sprite.Group()
    
  @property
  def army(self):
    return self.battle.armies[self.armyid]

  def _get_input(self, pause_str, accepted_inputs):
    pg.event.clear()
    while True:
      event = pg.event.wait()
      if event.type == pg.QUIT:
        pg.quit()
        sys.exit()
      elif event.type == pg.KEYDOWN:
        kn = pg.key.name(event.key)
        if kn.upper() in accepted_inputs:
          return kn.upper()

  def pause_and_display(self, pause_str=None):
    if self.automated:
      return
    self.draw()
    pg.event.clear()
    while True:
      event = pg.event.wait()
      if event.type == pg.KEYDOWN:
        return

  def new(self):
    self.background = Static(0, 0, resources.IMAGE_PATH / "old-paper-800-600.jpg")
    self.all_sprites.add(self.background)
    armies = self.battle.armies
    for j in range(2):
      v_offset = 120+240*j
      army = armies[j]
      for i, unit in enumerate(army.units):
        h_offset = 90 + 170*i
        spr = UnitSpr(h_offset, v_offset, resources.SPRITES_PATH / "Soldier.png", unit)
        self.all_sprites.add(spr)
    self.run()
    
  def events(self):
    pass

  def update(self):
    self.all_sprites.update()

  def draw(self, pause_str=None):
    if self.automated:
      return

    if self.playing:

      # if self.huddle_buf:
      #   self._render_and_pause_huddle()
      # if self.order_buf:
      #   self._render_and_pause_order()

      self.screen.fill(c.BLACK)

      # for armies, put them in sprites
      self.all_sprites.draw(self.screen)
      
      # we can ignore the statline
      # st = self._disp_statline()

      # we can just print an area for the console
      # co = self._disp_console() 
      # fo = self._disp_footerline(pause_str) # 1 line, string
      # meat = ar + st + co # meat of the print job, not counting the final string
      # assert len(meat) == self.max_screen_len - 1
      # # effects = []
      # for y, li in enumerate(meat):
      #   print(self._render(li))
      #   print(self._render(fo), end="", flush=True)
      #   self.console_buf = []

      pg.display.flip()

  def run(self):
    while self.playing:
      # self.clock.tick(self.fps)
      self.events()
      self.update()
      self.draw()

  def disp_chara_speech(self, chara, speech, context):
    """
    What to display when a character says something.
    """
    self.yprint("{}: '$[2]${}$[7]$'".format(chara.color_name(), speech),
                templates=context)

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
    if templates:
      converted_templates = convert_templates(templates)
      converted_text = text.format(**converted_templates)
    else:
      converted_text = text
    logging.debug(converted_text) # always log this
    if debug and not self.debug_mode:
      return
    # so we get here if either SHOW_DEBUG or debug=False, which means we send it to the buffer
    # right now: DO NOTHING
    # so we get here if either SHOW_DEBUG or debug=False, which means we send it to the buffer
    for m in mode:
      if m == "console":
        self.print_line(converted_text)
      elif m == "huddle":
        self.huddle_buf.append(converted_text)
      elif m == 'order_phase':
        self.order_buf.append(converted_text)
      else:
        assert m == 'AI'
        if self.show_AI:
          self.huddle_buf.append(converted_text)
    logging.info(text)

  
