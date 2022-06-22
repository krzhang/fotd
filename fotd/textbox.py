import pygame
import pygame.freetype
pygame.freetype.init()

from colors import PColors, color_bool, YCodes
from ytext import YText, disp_text_activation, disp_bar_custom

from settings_pygame import *
import settings_battle
import resources
import skills

from templates import text_convert

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



class TextBox:

  def __init__(self, view, width, height):
    self.tx = 0 # this is where the "cursor" is
    self.ty = 0
    self.view = view
    self.font_mid = pygame.freetype.Font(None, 20)
    self.font_small = pygame.freetype.Font(None, 12)
    self.surface = pygame.Surface((width, height))

  def clear(self):
    # these are the "cursors"
    self.surface.fill(PColors.BLACK)
    self.tx = 0
    self.ty = 0

  def text_to_surface(self, font, ytext_str):
    """ 
    Given a YText string and a pygame [surface], render the text to it (with colors).

    We return the final place for the cursor (only y is really important, since it tells us if
    we shifted vertically) 
  
    useful picture for font:
    https://user-images.githubusercontent.com/41798797/53959995-0e870780-4120-11e9-84b5-1dde7fa995ec.png

    See https://www.pygame.org/docs/ref/freetype.html#pygame.freetype.Font.render_to

    For styles, see https://www.pygame.org/docs/ref/freetype.html#pygame.freetype.Font.style
    """
    surf = self.surface
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
      if self.tx + bounds.width + bounds.x >= width:
        self.tx, self.ty = 0, self.ty + line_spacing
      style = pygame.freetype.STYLE_DEFAULT
      if attrs[i][2] == 1: # BOLD
        style = pygame.freetype.STYLE_STRONG
      font.render_to(surf, (self.tx, self.ty + line_spacing), None, fgcolor=attrs[i][0], bgcolor=attrs[i][1], style=style)
      self.tx += bounds.width
    self.tx = 0
    self.ty += line_spacing

    
class InfoBox(TextBox):
  """ the box on the right that shows mouseover info """

  def __init__(self, view):
    super().__init__(view, INFO_WIDTH, INFO_HEIGHT)

  def _day_status_str(self):
    """ Date and weather """
    return "Day {}: {}".format(self.view.battle.date, self.view.battle.weather)

  def _vs_str(self):
    """ Armies, Morale, placed Formations, orders, etc. """
    bat = self.view.battle
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
    active_skillcards = [sc.str_seen_by_army(self.view.army) for sc in unit.army.tableau.bulbed_by(unit)]
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
    self.clear()
    self.text_to_surface(self.font_mid, self._day_status_str())
    self.text_to_surface(self.font_mid, self._vs_str())

  def _render_unit(self, unit):
    self.clear()
    self.text_to_surface(self.font_mid, unit.character.full_name_fancy())
    self.text_to_surface(self.font_mid, self._disp_unit_healthline(unit, 0))
    self.text_to_surface(self.font_mid, self._disp_unit_status_noskills(unit))
    self.text_to_surface(self.font_mid, self._disp_unit_skills(unit, unit.army.armyid))
    
  def handle_info(self, info):
    if not info:
      self._render_default()
    elif info[0] == "UNIT":
      self._render_unit(info[1])

class Huddle(TextBox):
  """ 
  an overlay for huddle-related info; right now we will make it show up in the middle.

  Used to show huddle and orders.
  """

  def __init__(self, view):
    super().__init__(view, HUDDLE_WIDTH, HUDDLE_HEIGHT)
    self.font_large = pygame.freetype.Font(resources.FONTS_PATH / 'Mastji/Mastji.ttf', 32)
    self.lines_max = 20
    self.huddle_buf = []
    self.order_buf = []

  def _huddle_header_str(self):
    return text_convert("{ctarget_army}'s strategy session",
                        templates={'ctarget_army':self.view.army})
    
  def render(self, target):
    """ [target] can be "order" or "huddle" """
    self.clear()
    if target == "huddle":
      buf = self.huddle_buf
    else:
      assert target == "order"
      buf = self.order_buf
    # self.text_to_surface(self.surface, x, y, self.font_large, self._disp_statline())
    if target == "huddle":
      self.text_to_surface(self.font_large, self._huddle_header_str())
    else:
      assert target == "order"
      self.text_to_surface(self.font_large, "Order phase playout:")
    for i in range(self.lines_max):
      if buf:
        self.text_to_surface(self.font_mid, buf[0])
        buf.pop(0)
      else:
        self.text_to_surface(self.font_mid, "")
    if buf:
      self.view.pause()
  
class Console(TextBox):
  """ the box on the bottom that shows updates """

  def __init__(self, view): 
    super().__init__(view, CONSOLE_WIDTH, CONSOLE_HEIGHT)
    self.max_console_lines = 10
    self.font_large = pygame.freetype.Font(resources.FONTS_PATH / 'Mastji/Mastji.ttf', 32)
    self.console_buf = []

  def render(self):
    self.clear()
    for i in range(self.max_console_lines):
      if self.console_buf:
        self.text_to_surface(self.font_mid, self.console_buf[0])
        self.console_buf = self.console_buf[1:]
      else:
        self.text_to_surface(self.font_mid, "")
    if self.console_buf:
      self.view.pause()

class StateBox(TextBox):
  """ the lower-right corner to tell the player what's going on """
  def __init__(self, view):
    super().__init__(view, STATE_WIDTH, STATE_HEIGHT)
    self.font_large = pygame.freetype.Font(resources.FONTS_PATH / 'Mastji/Mastji.ttf', 32)
    self.view = view

  def render(self):
    self.clear()
    cur_state = self.view.battle.state_stack[-1]
    self.text_to_surface(self.font_large, str(cur_state))
