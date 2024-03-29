"""
pygame related abstractions. The main thing here is PGBattleScreen, which
is a kind of view and replaces the ASCII one in battleview.
"""
import logging
import sys
import os

import pygame
import pygame.freetype
pygame.freetype.init()

from pgsettings import *
import resources


from colors import PColors as c
from colors import color_bool, YCodes
from textutils import YText

import rps
import skills
import battle_constants
import state
from narration import BattleNarrator


# move to settings later

BASE_DIR = os.getcwd()
# RESOURCES_DIR = os.path.join(BASE_DIR, "Resources")
TITLE = "Battle"

from sprites import *
from templates import CONVERT_TEMPLATES_DISPS, convert_templates

PAUSE_STRS = {
  # "MORE_STR": Colors.INVERT + "MORE... [hit a key]" + Colors.ENDC,
  # "FORMATION_ORDER": Colors.INVERT +  "Input $[4]$FORMATION" + Colors.INVERT + " for army {armyid}$[7]$",
  # "FINAL_ORDER": Colors.INVERT + "Input $[4]$ORDERS" + Colors.INVERT + " for army {armyid}$[7]$"
  "MORE_STR": "MORE... [hit a key]",
  "FORMATION_ORDER": "Input Formation",
  "FINAL_ORDER": "Input Orders"
}

def disp_bar_custom(colors, chars, nums):
  """
  all iterators, to make bars like this: '####$$$$----@@@@@@@@' etc.
  k colors
  k chars
  k nums
  the nums are meant to go from large to small, so max size first, etc.
  """
  makestr = ""
  for i in zip(colors, chars, nums):
    makestr += i[0]
    makestr += i[1]*i[2]
  return makestr

def disp_bar_day_tracker(max_pos, base, last_turn, cur):
  return disp_bar_custom([YCodes.GOOD, YCodes.RED, YCodes.GREY, YCodes.GREY],
                         ['#', '#', '.', " "],
                         [cur, last_turn-cur, base-last_turn, max_pos-base])

def disp_text_activation(any_str, success=None, upper=True):
  """
  to display an ``activated'' string (skill, skillcard, whatever) to give a decorated 
  context.
  """
  if upper:
    newstr = any_str.upper()
  else:
    newstr = any_str
  # return "<" + colors.color_bool(success) + " ".join(newstr.split("_")) + "$[7]$>"
  return "<" + color_bool(success) + " ".join(newstr.split("_")) + "$[7]$>"

def text_to_surface(surf, x, y, font, ytext_str):
  """ 
  Given a YText string and a pygame [surface], render the text to it (with colors).

  We return the final place for the cursor (only y is really important, since it tells us if
  we shifted vertically) 
  
  useful picture for font:
  https://user-images.githubusercontent.com/41798797/53959995-0e870780-4120-11e9-84b5-1dde7fa995ec.png

  Return the offset for where the "cursor" should be next

  See https://www.pygame.org/docs/ref/freetype.html#pygame.freetype.Font.render_to
  """
  font.origin = True
  # this means everything is with respect to the origin. See link at beginning
  # of file for details
  ytext = YText(ytext_str)
  text, attrs = ytext.raw_str, ytext.pcolor_map
  width, height = surf.get_size()
  line_spacing = font.get_sized_height() + 2
  for i, t in enumerate(text):
    bounds = font.get_rect(t)
    if x + bounds.width + bounds.x >= width:
      x, y = 0, y + line_spacing    
    font.render_to(surf, (x, y + line_spacing), None, fgcolor=attrs[i][0], bgcolor=attrs[i][1])
    x += bounds.width
  return 0, y + line_spacing # the new cursor has things shifted

class InfoBox:
  """ the box on the right that shows mouseover info """

  def __init__(self, battlescreen):
    # upper-left-corner
    self.x = BG_WIDTH
    self.y = 0
    self.font_mid = pygame.freetype.Font(None, 20)
    self.font_small = pygame.freetype.Font(None, 12)
    # self.font_mid = pygame.freetype.Font(resources.FONTS_PATH / 'Mastji/Mastji.ttf', 20)
    # self.font_small = pygame.freetype.Font(resources.FONTS_PATH / 'Mastji/Mastji.ttf', 12)
    self.battlescreen = battlescreen
    self.surface = pygame.Surface((INFO_WIDTH, INFO_HEIGHT))

  def _disp_unit_healthline(self, unit, side):
    last_turn_size = unit.last_turn_size or unit.size_base
    healthbar = disp_bar_day_tracker(battle_constants.ARMY_SIZE_MAX,
                                     unit.size_base,
                                     last_turn_size,
                                     unit.size)
    statuses = self._disp_unit_status_noskills(unit)
    charstr = "{}/{} {}".format(unit.size, unit.size_base, healthbar)
    return charstr
  
  def _disp_unit_status_noskills(self, unit):
    """ string for the unit's statuses that do NOT include skills"""
    return " ".join((s.stat_viz() for s in unit.unit_status if not s.is_skill()))
  
  def _disp_unit_skills(self, unit, side):
    # inactive means skills that are not bulbed
    inactive_skillist = [s.str_fancy(success=False)
                         for s in unit.character.skills if
                         not bool(skills.skill_info(s.skill_str, 'activation') == 'passive')]
    inactive_skillstr = " ".join(inactive_skillist)
    # 'passive' means skills that are used and are not bulbed, meaning they *are* active
    active_skillist = [disp_text_activation(('*:' + s.short()),
                                              success=None, upper=False)
                       for s in unit.character.skills if
                       bool(skills.skill_info(s.skill_str, 'activation') == 'passive')]
    active_skillcards = [sc.str_seen_by_army(self.army) for sc in unit.army.tableau.bulbed_by(unit)]
    if inactive_skillstr:
      sepstr = " | "
    else:
      sepstr = "| "
    active_skillstr = " ".join(active_skillist + active_skillcards)
    charstr = " "*2 + active_skillstr
    return charstr
  
  def _render_unit(self, unit):
    self.surface.fill(c.BLACK)
    x, y = 0, 0
    x, y = text_to_surface(self.surface, x, y, self.font_mid, unit.character.full_name_fancy())
    x, y = text_to_surface(self.surface, x, y, self.font_mid, self._disp_unit_healthline(unit, 0))
    x, y = text_to_surface(self.surface, x, y, self.font_mid, self._disp_unit_status_noskills(unit))
    x, y = text_to_surface(self.surface, x, y, self.font_mid, self._disp_unit_skills(unit, unit.army.armyid))
    
  def handle_info(self, info):
    if not info:
      return
    if info[0] == "UNIT":
      self._render_unit(info[1])

class Console:
  """ the box on the bottom that shows updates """

  def __init__(self, battlescreen):
    # upper-left-corner
    self.x = 0
    self.y = BG_HEIGHT
    self.max_console_lines = 10
    self.font_large = pygame.freetype.Font(resources.FONTS_PATH / 'Mastji/Mastji.ttf', 32)
    self.font_mid = pygame.freetype.Font(resources.FONTS_PATH / 'Mastji/Mastji.ttf', 20)
    self.font_small = pygame.freetype.Font(resources.FONTS_PATH / 'Mastji/Mastji.ttf', 12)
    self.battlescreen = battlescreen
    self.surface = pygame.Surface((CONSOLE_WIDTH, CONSOLE_HEIGHT))
    self.console_buf = []

  def _day_status_str(self):
    """ what to put on top"""
    return "Day {}: {}".format(self.battlescreen.battle.date, self.battlescreen.battle.weather)

  def _vs_str(self):
    if self.battle.formations[0] and self.battle.formations[1]: # formation orders were given
      form0 = self.battle.formations[0].color_abbrev()
      form1 = self.battle.formations[1].color_abbrev()
    else:
      form0 = form1 = "?"
    if self.battle.orders[0] and self.battle.orders[1]:
      strat0 = self.battle.orders[0].color_abbrev()
      strat1 = self.battle.orders[1].color_abbrev()
    else:
      strat0 = strat1 = "?"
    if self.battle.yomi_winner_id == -1:
      winner_text = "$[7,2]$VS$[7]$"
    elif self.battle.yomi_winner_id == 0:
      winner_text = "$[7,1]$>>$[7]$"
    else:
      winner_text = "$[7,1]$<<$[7]$"
    return "      {} ({}) {} -> {} {} {} <- {} ({}) {}".format(
      disp_bar_morale(10, self.battle.armies[0].morale, self.battle.armies[0].last_turn_morale),
      self.battle.armies[0].color_name(),
      form0,
      strat0,
      winner_text,
      strat1,
      form1,
      self.battle.armies[1].color_name(),
      disp_bar_morale(10, self.battle.armies[1].morale, self.battle.armies[1].last_turn_morale))
  
  def _disp_statline(self): # 3 lines
    vs_line = self._vs_str()
    statline = self._day_status_str()
    return [statline, vs_line]
    
  def render(self):
    self.surface.fill(c.BLACK)
    to_print = []
    x, y = 0, 0
    # x, y = text_to_surface(self.surface, x, y, self.font_large, self._disp_statline())
    x, y = text_to_surface(self.surface, x, y, self.font_large, self._day_status_str())
    for i in range(self.max_console_lines):
      if self.console_buf:
        x, y = text_to_surface(self.surface, x, y, self.font_mid, self.console_buf[0])
        self.console_buf = self.console_buf[1:]
      else:
        x, y = text_to_surface(self.surface, x, y, self.font_mid, "")
    if self.console_buf:
      self.battlescreen.pause()

      # we can ignore the statline for now
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

class StateBox:
  """ the lower-right corner to tell the player what's going on """
  def __init__(self, battlescreen):
    # upper-left-corner
    self.x = BG_WIDTH
    self.y = BG_HEIGHT
    self.font_large = pygame.freetype.Font(resources.FONTS_PATH / 'Mastji/Mastji.ttf', 32)
    self.font_mid = pygame.freetype.Font(resources.FONTS_PATH / 'Mastji/Mastji.ttf', 20)
    self.font_small = pygame.freetype.Font(resources.FONTS_PATH / 'Mastji/Mastji.ttf', 12)
    self.battlescreen = battlescreen
    self.surface = pygame.Surface((STATE_WIDTH, STATE_HEIGHT))

  def render(self):
    self.surface.fill(c.BLACK)
    cur_state = self.battlescreen.battle.state_stack[-1]
    text_to_surface(self.surface, 0, 0, self.font_large, str(cur_state))

class PGBattleScreen:
  """ a Pygame View + Controller for a battle object """

  def __init__(self, battle, armyid, automated=False, show_AI=False):
    self.game_width, self.game_height = WIDTH, HEIGHT
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" % (50, 50)

    self.screen = pygame.display.set_mode((self.game_width, self.game_height))
    pygame.display.set_caption(TITLE)

    # self.clock = pygame.time.clock()
    self.running = True
    self.playing = True
    self.fps = FPS

    pygame.font.init()
    pygame.mixer.init()

    self.battle = battle
    
    self.infobox = InfoBox(self)
    self.console = Console(self)
    self.statebox = StateBox(self)
    self.narrator = BattleNarrator(self.battle, self)
    
    self.huddle_buf = []
    self.order_buf = []

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
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.playing = False
      if event.type == pygame.KEYDOWN:
        kr = pygame.key.name(event.key)
        kn = kr.upper()
        print(kn)
        if kn in self.actions:
          self.actions[kn] = True
          if kn == 'Q':
            pygame.quit()
            sys.exit(0)
        
  def update(self):
    self.all_sprites.update()
    self.state_stack[-1].update(self.actions)

  def draw(self, pause_str=None):
    if self.automated:
      return

    if self.playing:

      # if self.huddle_buf:
      #   self._render_and_pause_huddle()
      # if self.order_buf:
      #   self._render_and_pause_order()

      self.screen.fill(c.BLACK)

      # sprites
      self.all_sprites.draw(self.screen)

      # infobox
      mouseover = None
      for spr in self.all_sprites:
        if spr.infobox and spr.rect.collidepoint(pygame.mouse.get_pos()):
          mouseover = spr.mouseover_info()
          break

      if mouseover:
        self.infobox.handle_info(mouseover)
        self.screen.blit(self.infobox.surface, (BG_WIDTH, 0))

      # console
      self.console.render()
      self.screen.blit(self.console.surface, (0, BG_HEIGHT))

      # state
      self.statebox.render()
      self.screen.blit(self.statebox.surface, (BG_WIDTH, BG_HEIGHT))

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
    for i, healths in enumerate(health_history[1:]):
      bars = [None, None]
      for j in [0, 1]:
        last_health = health_history[i][j]
        bars[j] = disp_bar_custom([YCodes.CYAN, YCodes.RED, YCodes.GREY],
                                  ['=', '*', '.'],
                                  [healths[j], last_health - healths[j], 20 - last_health])
      self.yprint("   {} {} vs {} {}".format(csource.color_name(),
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
    if templates:
      converted_templates = convert_templates(templates)
      converted_text = text.format(**converted_templates)
    else:
      converted_text = text
    logging.debug(converted_text) # always log this
    if debug and not self.debug_mode:
      return
    # so we get here if either SHOW_DEBUG or debug=False, which means we send it to the buffer
    for m in mode:
      if m == "console":
        self.console.console_buf.append(converted_text)
      elif m == "huddle":
        self.huddle_buf.append(converted_text)
      elif m == 'order_phase':
        self.order_buf.append(converted_text)
      else:
        assert m == 'AI'
        if self.show_AI:
          self.huddle_buf.append(converted_text)
