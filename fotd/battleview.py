"""
The View is something that takes care of all rendering-related tasks,
so it is the view in MVC. This file is for the default text (Asciimatics)
based view.
"""

import logging

import settings_battle
import duel

from colors import ctext, YCodes
import colors
from ytext import YText

import narration
import rps
import skills
from templates import CONVERT_TEMPLATES_DISPS, convert_templates

######
# IO #
######

PAUSE_STRS = {
  "MORE_STR": "MORE... [hit a key]",
  "FORMATION_ORDER": "Input $[4]$FORMATION for army {armyid}$[7]$",
  "FINAL_ORDER": "Input $[4]$ORDERS for army {armyid}$[7]$" 
}

#######################
# Text Mode Utilities #
#######################

def read_single_keypress():
  """Waits for a single keypress on stdin.

  [How do I make python to wait for a pressed key - Stack Overflow](https://stackoverflow.com/questions/983354/how-do-i-make-python-to-wait-for-a-pressed-key#comment90923542_6599441)

  This is a silly function to call if you need to do it a lot because it has
  to store stdin's current setup, setup stdin for reading single keystrokes
  then read the single keystroke then revert stdin back after reading the
  keystroke.
  
  Returns a tuple of characters of the key that was pressed - on Linux, 
  pressing keys like up arrow results in a sequence of characters. Returns 
  ('\x03',) on KeyboardInterrupt which can happen when a signal gets
  handled.
  
  """
  import termios, fcntl, sys
  fd = sys.stdin.fileno()
  # save old state
  flags_save = fcntl.fcntl(fd, fcntl.F_GETFL)
  attrs_save = termios.tcgetattr(fd)
  # make raw - the way to do this comes from the termios(3) man page.
  attrs = list(attrs_save) # copy the stored version to update
  # iflag
  attrs[0] &= ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK
                | termios.ISTRIP | termios.INLCR | termios. IGNCR
                | termios.ICRNL | termios.IXON )
  # oflag
  attrs[1] &= ~termios.OPOST
  # cflag
  attrs[2] &= ~(termios.CSIZE | termios. PARENB)
  attrs[2] |= termios.CS8
  # lflag
  attrs[3] &= ~(termios.ECHONL | termios.ECHO | termios.ICANON
                | termios.ISIG | termios.IEXTEN)
  termios.tcsetattr(fd, termios.TCSANOW, attrs)
  # turn off non-blocking
  fcntl.fcntl(fd, fcntl.F_SETFL, flags_save & ~os.O_NONBLOCK)
  # read a single keystroke
  ret = []
  try:
    ret.append(sys.stdin.read(1)) # returns a single character
    fcntl.fcntl(fd, fcntl.F_SETFL, flags_save | os.O_NONBLOCK)
    c = sys.stdin.read(1) # returns a single character
    while len(c) > 0:
      ret.append(c)
      c = sys.stdin.read(1)
  except KeyboardInterrupt:
    ret.append('\x03')
  finally:
    # restore old state
    termios.tcsetattr(fd, termios.TCSAFLUSH, attrs_save)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags_save)
  if ret[0] == 'q':
    sys.exit(0)
  return tuple(ret)

def clear_screen():
  os.system('cls' if os.name == 'nt' else 'clear')

###################
# Base View class # (TODO: move out later when we have more views
###################

class View():

  def __init__(self, automated=False):
    self.automated = automated

  def _render(self, line):
    """
    converts a line of my-type of string (see prerender) to step 2, which is colorama-printable
    """
    return YText(line).to_pygame()

  def _flush(self):
    pass
  
  def render_all(self):
    pass

  def _get_input(self, pause_str, accepted_inputs):
    # this part screws with MVC a bit
    while True:
      self.render_all(pause_str=pause_str)
      inp = read_single_keypress()[0]
      if inp.upper() in accepted_inputs:
        return inp.upper()

  def pause_and_display(self, pause_str=None):
    if self.automated:
      return
    self.render_all(pause_str=pause_str)
    _ = read_single_keypress()[0]
    self._flush()

#########################################
# Display (convert to string) Functions #
#########################################

def disp_hrule():
  return "="*80

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

def disp_text_activation(any_str, success=None, upper=True):
  """
  to display an ``activated'' string (skill, skillcard, whatever) to give a decorated 
  context.
  """
  if upper:
    newstr = any_str.upper()
  else:
    newstr = any_str
  return "<" + colors.color_bool(success) + " ".join(newstr.split("_")) + "$[7]$>"
    
#########################
# Battle-specific stuff #
#########################

def disp_damage_calc(s_str, d_str, dicecount, hitprob, raw_damage):
  return "[Strength: ({:4.3f} vs. {:4.3f}); {} dice with chance {} each; Final: {}]".format(
    s_str, d_str, dicecount, colors.color_prob(hitprob), colors.color_damage(raw_damage))

def disp_form_short(formation):
  return rps.formation_info(formation, "short")

def disp_unit_status_noskills(unit):
  """ string for the unit's statuses that do NOT include skills"""
  return " ".join((s.stat_viz() for s in unit.unit_status if not s.is_skill()))

def disp_bar_morale(max_morale, cur_morale, last_turn_morale):
  if last_turn_morale > cur_morale:
    return disp_bar_custom([YCodes.BLUE, YCodes.FAILURE, YCodes.GREY],
                           ['+', '*', '.'],
                           [cur_morale, last_turn_morale-cur_morale, max_morale-last_turn_morale])
  return disp_bar_custom([YCodes.BLUE, YCodes.SUCCESS, YCodes.GREY],
                         ['+', '*', '.'],
                         [last_turn_morale, cur_morale-last_turn_morale, max_morale-cur_morale])

def disp_bar_single_hit(max_pos, oldhp, newhp):
  """Total: length; base: max; cur: current. """
  return disp_bar_custom([YCodes.SUCCESS, YCodes.RED, YCodes.GREY],
                         ['#', '#', ' '],
                         [newhp, oldhp-newhp, max_pos-oldhp])
  # return  YCodes.OKGREEN + '#'*cur + YCodes.RED + '#'*(base-cur) + YCodes.GREY + '.'*(total-base)

def disp_bar_day_tracker(max_pos, base, last_turn, cur):
  return disp_bar_custom([YCodes.GOOD, YCodes.RED, YCodes.GREY, YCodes.GREY],
                         ['#', '#', '.', " "],
                         [cur, last_turn-cur, base-last_turn, max_pos-base])

class MockBattleView(View):
  """
  a mock view (for e.g. AI imagination where we need no output)
  """
  
  def __init__(self, battle, armyid, automated=False, show_AI=False):
    super().__init__(automated=automated)
    self.battle = battle
    self.debug_mode = self.battle.debug_mode
    self.armyid = armyid
    self.show_AI = show_AI
    self.narrator = narration.BattleNarrator(self.battle, self)

  @property
  def army(self):
    return self.battle.armies[self.armyid]
  
  def render_all(self, pause_str=None):
    pass
  
  def disp_duel(self, csource, ctarget, loser_history, health_history, damage_history):
    pass

  def disp_chara_speech(self, chara, speech, context):
    """
    What to display when a character says something.
    """
    pass
  
  def disp_activated_narration(self, activated_text, other_str, success=None):
    """ 
    What to display when we want to make a narration involving a skill / skillcard
    (really any string)
    """
    pass
  
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

  def pause(self):
    pass

  ############
  # Printing #
  ############
  
  def print_line(self, text):
    logging.info(text)

  def yprint(self, text, templates=None, debug=False, mode=("console",)):
    logging.info(text)

class TextBattleView(View):
  """ 
  Default ASCII-oriented View. 
  """
  def __init__(self, battle, armyid, automated=False, show_AI=False):
    super().__init__(automated=automated)
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
    self.show_AI = show_AI

  def _flush(self):
    self.console_buf = []
    self.huddle_buf = []
    self.order_buf = []
    
  @property
  def army(self):
    return self.battle.armies[self.armyid]
  
  def _colored_strats(self, orders):
    orders = list(orders)
    ocolors = []
    for i in [0,1]:
      other = 1-i
      if rps.beats(orders[i], orders[other]):
        ocolors.append(YCodes.SUCCESS)
      elif rps.beats(orders[other], orders[i]):
        ocolors.append(YCodes.FAILURE)
      else:
        ocolors.append("")
    return tuple([ocolors[i] + orders[i] + YCodes.GREY for i in [0,1]])

  def _day_status_str(self):
    """ what to put on top"""
    return "Day {}: {}".format(self.battle.date, self.battle.weather)

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

  def _disp_unit_healthline(self, unit, side):
    healthbar = disp_bar_day_tracker(settings_battle.ARMY_SIZE_MAX, unit.size_base, unit.last_turn_size, unit.size)
    statuses = disp_unit_status_noskills(unit)
    # charstr = "{} {} Hp:{} {}".format(healthbar, disp_cha_fullname(unit.character),
    #                                   disp_unit_size(unit), statuses)
    charstr = "{} {} {}".format(healthbar, unit.character.full_name_fancy(), statuses)
    return charstr

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

  def _disp_armies(self): # 17 lines
    battle = self.battle
    armies_buf = []
      
    for j in [0,1]:
      for i in range(4):
        if len(battle.armies[j].present_units()) > i:
          unit = battle.armies[j].present_units()[i]
          header = self._disp_unit_healthline(unit, j)
          situ = self._disp_unit_skills(unit, j)
        else:
          header = ""
          situ = ""
        armies_buf.append(header)
        armies_buf.append(situ)
    armies_buf.append(disp_hrule())
    return armies_buf

  def _disp_statline(self): # 3 lines
    vs_line = self._vs_str()
    statline = self._day_status_str()
    return [statline, vs_line, disp_hrule()]
  
  def _disp_console(self):
    newbuf = []
    for i in range(self.max_console_len):
      if i < len(self.console_buf):
        newbuf.append(self.console_buf[i])
      else:
        newbuf.append("")
    return newbuf

  def _disp_footerline(self, pause_str):
    if pause_str:
      return(pause_str)
    else:
      return(disp_hrule())

  def _disp_huddle_header(self):
    self.yprint("{ctarget_army}'s strategy session", templates={'ctarget_army':self.army},
                mode=["huddle"])
    self.yprint(disp_hrule(), mode=["huddle"])
    self.huddle_buf = self.huddle_buf[-2:] + self.huddle_buf[:-2]  # such a hack

  def _render_and_pause_huddle(self):
    """
    render and clear the 'huddle' buffer used for displaying huddle information
    """
    clear_screen()
    self._disp_huddle_header()
    for y, li in enumerate(self.huddle_buf):
      print(self._render(li))
    while (y < self.max_screen_len-2):
      print("")
      y += 1
    print(self._render(self._disp_footerline(pause_str=PAUSE_STRS["MORE_STR"])),
          end="", flush=True)
    _ = read_single_keypress()[0]
    self.huddle_buf = []

  def _disp_order_header(self):
    self.yprint("order phase playout",
                mode=["order_phase"])
    self.yprint(disp_hrule(), mode=["order_phase"])
    self.order_buf = self.order_buf[-2:] + self.order_buf[:-2]  # such a hack

  def _render_and_pause_order(self):
    """
    order phase
    """
    clear_screen()
    self._disp_order_header()
    for y, li in enumerate(self.order_buf):
      print(self._render(li))
    while (y < self.max_screen_len-2):
      print("")
      y += 1
    print(self._render(self._disp_footerline(pause_str=PAUSE_STRS["MORE_STR"])),
          end="", flush=True)
    _ = read_single_keypress()[0]
    self.order_buf = []
    
  def render_all(self, pause_str=None):
    # blits status
    if self.automated:
      return
    if self.huddle_buf:
      self._render_and_pause_huddle()
    if self.order_buf:
      self._render_and_pause_order()
    clear_screen()
    ar = self._disp_armies() 
    st = self._disp_statline() 
    co = self._disp_console() 
    fo = self._disp_footerline(pause_str) # 1 line, string
    meat = ar + st + co # meat of the print job, not counting the final string
    assert len(meat) == self.max_screen_len - 1
    # effects = []
    for y, li in enumerate(meat):
      print(self._render(li))
    print(self._render(fo), end="", flush=True)
    self.console_buf = []

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

  def disp_chara_speech(self, chara, speech, context):
    """
    What to display when a character says something.
    """
    self.yprint("{}: '$[2]${}$[7]$'".format(chara.color_name(), speech),
                templates=context)
  
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
  
  def print_line(self, text):
    assert len(self.console_buf) <= self.max_console_len
    if len(self.console_buf) == self.max_console_len:
      # about to fill
      self.pause_and_display(pause_str=PAUSE_STRS["MORE_STR"])
    self.console_buf.append(text)
    logging.info(text)

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
