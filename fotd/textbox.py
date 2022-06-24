import pygame
import pygame.freetype
pygame.freetype.init()

from colors import PColors, color_bool, YCodes
from ytext import YText, disp_text_activation, disp_bar_custom

from settings_pygame import *
import settings_battle

import state

import resources
import skills
import battle

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

  def __init__(self, view, width, height, name, header=""):
    self.tx = 0 # this is where the "cursor" is
    self.ty = 0
    self.view = view
    self.font_large = pygame.freetype.Font(None, 32)
    self.font_mid = pygame.freetype.Font(None, 20)
    self.font_small = pygame.freetype.Font(None, 12)
    self.surface = pygame.Surface((width, height))
    self.name = name
    self.header = header
    
  def clear(self):
    # these are the "cursors"
    self.surface.fill(PColors.BLACK)
    self.tx = 0
    self.ty = 0

  def get_current_state(self):
    return self.view.battle.state_stack[-1]
    
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

  def render(self):
    pass

  def update(self, actions):
    pass
    
class BufferTextBox(TextBox):
  """ This is a slightly extended Textbox that allows an internal buffer which pauses
  automatically when filled"""
  def __init__(self, view, width, height, name, lines_max, header=""):
    super().__init__(view, width, height, name)
    self.lines_max = lines_max
    self.header = header
    self.buf = []
    self.paused = False

  def render(self):
    if self.paused:
      return
    self.clear()
    if self.header:
      self.text_to_surface(self.font_large, self.header)
    for i in range(self.lines_max):
      if len(self.buf) > i:
        self.text_to_surface(self.font_mid, self.buf[i])
      else:
        self.text_to_surface(self.font_mid, "")
    if len(self.buf) >= self.lines_max:
      # self.view.pause(self, pause_str="[MORE ({})... ]".format(self.name))
      self.paused = True
      # this paused is a marker to self to not print more text.

  def update(self, actions):
    if (actions and any(actions.values())):
      # the first check is if actions is None (since we are async we could be catching it
      # before its infomation is filled)
      # we are not in a paused state, but we should still flush
      if len(self.buf) >= self.lines_max:
        self.buf = self.buf[self.lines_max:]
      else:
        self.buf = []
      self.paused = False
      self.clear()    
      
class InfoBox(TextBox):
  """ the box on the right that shows mouseover info """

  def __init__(self, view):
    super().__init__(view, INFO_WIDTH, INFO_HEIGHT, "info", 50)
    self.mouseover = None
    
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
                         (s.activation != 'passive')]
    inactive_skillstr = " ".join(inactive_skillist)
    # 'passive' means skills that are used and are not bulbed, meaning they *are* active
    active_skillist = [disp_text_activation(('*:' + s.short), success=None, upper=False)
                       for s in unit.character.skills if
                       (s.activation == 'passive')]
    active_skillcards = [sc.str_seen_by_army(self.view.army) for sc in unit.army.tableau.bulbed_by(unit)]
    if inactive_skillstr:
      sepstr = " | "
    else:
      sepstr = "| "
    active_skillstr = " ".join(active_skillist + active_skillcards)
    charstr = " "*2 + active_skillstr
    return charstr

  def _render_skill(self, skill):
    self.clear()
    self.text_to_surface(self.font_large, "Skill: " + skill.skill_str)
    self.text_to_surface(self.font_large, "")
    self.text_to_surface(self.font_mid, "Activation: " + skill.activation)
    self.text_to_surface(self.font_mid, "")
    self.text_to_surface(self.font_mid, skill.desc)
    if skill.skillcard:
      sc = skills.SkillCard(skill.skillcard)
      self.text_to_surface(self.font_mid, "")
      self.text_to_surface(self.font_large, "Skillcard: " +sc.sc_str)
      bulb_str = "Bulb rates: $[1]$A$[7]$:{}, $[4]$A$[7]$:{}, $[3]$A$[7]$:{}".format(sc.bulb['A'], sc.bulb['D'], sc.bulb['I'])
      self.text_to_surface(self.font_mid, "")
      self.text_to_surface(self.font_mid, bulb_str)
      self.text_to_surface(self.font_mid, sc.desc)
  
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

  def render(self):
    if not self.mouseover:
      self._render_default()
    elif self.mouseover[0] == "UNIT":
      self._render_unit(self.mouseover[1])
    elif self.mouseover[0] == "SKILL":
      self._render_skill(self.mouseover[1])
    elif self.mouseover[0] == "SKILLCARD":
      self._render_skill(self.mouseover[1])
      
class Huddle(BufferTextBox):
  """ 
  an overlay for huddle-related info; right now we will make it show up in the middle.

  Used to show huddle and orders.
  """

  def __init__(self, view, name, header):
    super().__init__(view, HUDDLE_WIDTH, HUDDLE_HEIGHT, name, 20, header=header)
    self.font_large = pygame.freetype.Font(resources.FONTS_PATH / 'Mastji/Mastji.ttf', 32)
      
class Console(BufferTextBox):
  """ the box on the bottom that shows updates """

  def __init__(self, view): 
    super().__init__(view, CONSOLE_WIDTH, CONSOLE_HEIGHT, "console", 10)
    self.font_large = pygame.freetype.Font(resources.FONTS_PATH / 'Mastji/Mastji.ttf', 32)
     
class StateBox(TextBox):
  """ the lower-right corner to tell the player what's going on """
  def __init__(self, view):
    super().__init__(view, STATE_WIDTH, STATE_HEIGHT, "state", 5)
    self.font_large = pygame.freetype.Font(resources.FONTS_PATH / 'Mastji/Mastji.ttf', 32)
    self.view = view

  def render(self):
    self.clear()
    cur_state = self.get_current_state()
    self.text_to_surface(self.font_large, str(cur_state))
    pause_str = ""
    if isinstance(cur_state, state.Pause):
      if cur_state.pause_str:
        pause_str = cur_state.pause_str
      else:
        pause_str = "[Press a key...]"
    elif isinstance(cur_state, battle.FormationTurn) or isinstance(cur_state, battle.OrderTurn):
      pause_str = "[$[1]$A / $[4]$D / $[3]$I...]"      
    self.text_to_surface(self.font_large, pause_str)
    self.text_to_surface(self.font_small, "[top elt: {}]".format(self.view._top_action_receiver()))
