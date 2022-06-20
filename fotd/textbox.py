import pygame
import pygame.freetype
pygame.freetype.init()

from colors import PColors, color_bool, YCodes
from ytext import YText, disp_text_activation

from settings_pygame import *
import resources

from templates import text_convert

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

def disp_bar_morale(max_morale, cur_morale, last_turn_morale):
  if last_turn_morale > cur_morale:
    return disp_bar_custom([YCodes.BLUE, YCodes.FAILURE, YCodes.GREY],
                           ['+', '*', '.'],
                           [cur_morale, last_turn_morale-cur_morale, max_morale-last_turn_morale])
  return disp_bar_custom([YCodes.BLUE, YCodes.SUCCESS, YCodes.GREY],
                         ['+', '*', '.'],
                         [last_turn_morale, cur_morale-last_turn_morale, max_morale-cur_morale])

def disp_bar_day_tracker(max_pos, base, last_turn, cur):
  return disp_bar_custom([YCodes.GOOD, YCodes.RED, YCodes.GREY, YCodes.GREY],
                         ['#', '#', '.', " "],
                         [cur, last_turn-cur, base-last_turn, max_pos-base])


def text_to_surface(surf, x, y, font, ytext_str):
  """ 
  Given a YText string and a pygame [surface], render the text to it (with colors).

  We return the final place for the cursor (only y is really important, since it tells us if
  we shifted vertically) 
  
  useful picture for font:
  https://user-images.githubusercontent.com/41798797/53959995-0e870780-4120-11e9-84b5-1dde7fa995ec.png

  Return the offset for where the "cursor" should be next

  See https://www.pygame.org/docs/ref/freetype.html#pygame.freetype.Font.render_to

  For styles, see https://www.pygame.org/docs/ref/freetype.html#pygame.freetype.Font.style
  """
  font.origin = True
  # this means everything is with respect to the origin. See link at beginning
  # of file for details
  ytext = YText(ytext_str)
  text, attrs = ytext.raw_str, ytext.pcolor_map
  # recall the triple is (foreground, background, attribute)
  width, height = surf.get_size()
  line_spacing = (font.get_sized_height() + 2)
  for i, t in enumerate(text):
    bounds = font.get_rect(t)
    if x + bounds.width + bounds.x >= width:
      x, y = 0, y + line_spacing
    style = pygame.freetype.STYLE_DEFAULT
    if attrs[i][2] == 1: # BOLD
      style = pygame.freetype.STYLE_STRONG
    font.render_to(surf, (x, y + line_spacing), None, fgcolor=attrs[i][0], bgcolor=attrs[i][1], style=style)
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
    self.battlescreen = battlescreen
    self.surface = pygame.Surface((INFO_WIDTH, INFO_HEIGHT))

  def _day_status_str(self):
    """ Date and weather """
    return "Day {}: {}".format(self.battlescreen.battle.date, self.battlescreen.battle.weather)

  def _vs_str(self):
    """ Armies, Morale, placed Formations, orders, etc. """
    bat = self.battlescreen.battle
    if bat.formations[0] and bat.formations[1]: # formation orders were given
      form0 = bat.formations[0].color_abbrev()
      form1 = bat.formations[1].color_abbrev()
    else:
      form0 = form1 = "?"
    if bat.orders[0] and bat.orders[1]:
      strat0 = bat.orders[0].color_abbrev()
      strat1 = bat.orders[1].color_abbrev()
    else:
      strat0 = strat1 = "?"
    if bat.yomi_winner_id == -1:
      winner_text = "$[7,2]$VS$[7]$"
    elif bat.yomi_winner_id == 0:
      winner_text = "$[7,1]$>>$[7]$"
    else:
      winner_text = "$[7,1]$<<$[7]$"
    p1 = "{} ({}) {} -> {}".format(disp_bar_morale(10,
                                                   bat.armies[0].morale,
                                                   bat.armies[0].last_turn_morale),
                                   bat.armies[0].color_name(),
                                   form0,
                                   strat0)
    p2 = " {}".format(winner_text)
    p3 = " {} <- {} ({}) {}".format(strat1,
                                    form1,
                                    bat.armies[1].color_name(),
                                    disp_bar_morale(10,
                                                    bat.armies[1].morale,
                                                    bat.armies[1].last_turn_morale))
    return p1 + p2 + p3
  
  def _disp_unit_healthline(self, unit, side):
    last_turn_size = unit.last_turn_size or unit.size_base
    healthbar = disp_bar_day_tracker(settings_battle.ARMY_SIZE_MAX,
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
    active_skillcards = [sc.str_seen_by_army(self.battlescreen.army) for sc in unit.army.tableau.bulbed_by(unit)]
    if inactive_skillstr:
      sepstr = " | "
    else:
      sepstr = "| "
    active_skillstr = " ".join(active_skillist + active_skillcards)
    charstr = " "*2 + active_skillstr
    return charstr

  def _render_default(self):
    """
    The default item to render if we aren't mousing over an important item. This would be
    things in the old statline, like weather, completed orders, etc. basically the battle state:
    """
    self.surface.fill(PColors.BLACK)
    x, y = 0, 0
    x, y = text_to_surface(self.surface, x, y, self.font_mid, self._day_status_str())
    x, y = text_to_surface(self.surface, x, y, self.font_mid, self._vs_str())

  def _render_unit(self, unit):
    self.surface.fill(PColors.BLACK)
    x, y = 0, 0
    x, y = text_to_surface(self.surface, x, y, self.font_mid, unit.character.full_name_fancy())
    x, y = text_to_surface(self.surface, x, y, self.font_mid, self._disp_unit_healthline(unit, 0))
    x, y = text_to_surface(self.surface, x, y, self.font_mid, self._disp_unit_status_noskills(unit))
    x, y = text_to_surface(self.surface, x, y, self.font_mid, self._disp_unit_skills(unit, unit.army.armyid))
    
  def handle_info(self, info):
    if not info:
      self._render_default()
    elif info[0] == "UNIT":
      self._render_unit(info[1])

class Huddle:
  """ an overlay for huddle-related info; right now we will make it show up in the middle  """

  def __init__(self, battlescreen):
    # upper-left-corner
    self.x = BG_WIDTH/4
    self.y = BG_HEIGHT/4
    self.max_huddle_lines = 20
    self.font_large = pygame.freetype.Font(resources.FONTS_PATH / 'Mastji/Mastji.ttf', 32)
    self.font_mid = pygame.freetype.Font(None, 20)
    self.font_small = pygame.freetype.Font(None, 12)
    self.battlescreen = battlescreen
    self.surface = pygame.Surface((HUDDLE_WIDTH, HUDDLE_HEIGHT))
    self.huddle_buf = []

  def _huddle_header_str(self):
    return text_convert("{ctarget_army}'s strategy session",
                        templates={'ctarget_army':self.battlescreen.army})
    
  def render(self):
    self.surface.fill(PColors.BLACK)
    to_print = []
    x, y = 0, 0
    # x, y = text_to_surface(self.surface, x, y, self.font_large, self._disp_statline())
    x, y = text_to_surface(self.surface, x, y, self.font_large, self._huddle_header_str())
    for i in range(self.max_huddle_lines):
      if self.huddle_buf:
        x, y = text_to_surface(self.surface, x, y, self.font_mid, self.huddle_buf[0])
        self.huddle_buf = self.huddle_buf[1:]
      else:
        x, y = text_to_surface(self.surface, x, y, self.font_mid, "")
    if self.huddle_buf:
      self.battlescreen.pause()
  
class Console(object):
  """ the box on the bottom that shows updates """

  def __init__(self, battlescreen):
    # upper-left-corner
    self.x = 0
    self.y = BG_HEIGHT
    self.max_console_lines = 10
    self.font_large = pygame.freetype.Font(resources.FONTS_PATH / 'Mastji/Mastji.ttf', 32)
    # self.font_mid = pygame.freetype.Font(resources.FONTS_PATH / 'Mastji/Mastji.ttf', 20)
    # self.font_small = pygame.freetype.Font(resources.FONTS_PATH / 'Mastji/Mastji.ttf', 12)
    self.font_mid = pygame.freetype.Font(None, 20)
    self.font_small = pygame.freetype.Font(None, 12)
    self.battlescreen = battlescreen
    self.surface = pygame.Surface((CONSOLE_WIDTH, CONSOLE_HEIGHT))
    self.console_buf = []


      
  def render(self):
    self.surface.fill(PColors.BLACK)
    to_print = []
    x, y = 0, 0
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
    # self.font_mid = pygame.freetype.Font(resources.FONTS_PATH / 'Mastji/Mastji.ttf', 20)
    # self.font_small = pygame.freetype.Font(resources.FONTS_PATH / 'Mastji/Mastji.ttf', 12)
    self.font_mid = pygame.freetype.Font(None, 20)
    self.font_small = pygame.freetype.Font(None, 12)
    self.battlescreen = battlescreen
    self.surface = pygame.Surface((STATE_WIDTH, STATE_HEIGHT))

  def render(self):
    self.surface.fill(PColors.BLACK)
    cur_state = self.battlescreen.battle.state_stack[-1]
    text_to_surface(self.surface, 0, 0, self.font_large, str(cur_state))
