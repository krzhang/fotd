# import graphics_asciimatics
from utils import read_single_keypress
import os
import logging
import colors
from colors import Colors, Colours, Fore, Back, Style

import sys
import rps

#########################################
# Display (convert to string) Functions #
#########################################

def disp_damage_calc(s_str, d_str, dicecount, hitprob, raw_damage):
  return "[Strength: ({:4.3f} vs. {:4.3f}); {} dice with chance {} each; Final: {}]".format(
    s_str, d_str, dicecount, colors.color_prob(hitprob), colors.color_damage(raw_damage))

def disp_cha_title(chara):
  if self.title:
    return " -={}=-".format(self.title) # eventually move out
  else:
    return ""

def disp_cha_fullname(chara):
  return str(chara) + chara.str_title()  

def disp_army(army):
  return "$[{}$]{}$[7$]".format(army.color, army.name)

def disp_form_short(formation):
  return rps.FORMATION_ORDERS[formation]["short"]

def disp_skill_activation(skill_str, success=None):
  return "<" + colors.color_bool(success) + " ".join(skill_str.upper().split("_")) + "$[7$]>"

def disp_order_short(order):
  return rps.STRATEGIC_ORDERS[order]["short"]

def disp_unit(unit):
  return "$[{}$]{}$[7$]".format(unit.color, unit.name)

def disp_unit_size(unit):
  csize = colors.color_size(unit.size, unit.size_base) + str(unit.size) + "$[7$]"
  return "{}/{}".format(str(csize), str(unit.size_base)) 

def disp_unit_status_noskills(unit):
  """ string for the unit's statuses that do NOT include skills"""
  return " ".join((str(s) for s in unit.unit_status if not s.is_skill()))

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
  
def disp_bar_single_hit(max_pos, oldhp, newhp):
  """Total: length; base: max; cur: current. """
  return disp_bar_custom([Colors.OKGREEN, Colors.RED, Colors.ENDC],
                         ['#', '#', ' '],
                         [newhp, oldhp-newhp, max_pos-oldhp ])
  # return  Colors.OKGREEN + '#'*cur + Colors.RED + '#'*(base-cur) + Colors.ENDC + '.'*(total-base)

def disp_bar_day_tracker(max_pos, base, last_turn, cur):
  return disp_bar_custom([Colors.OKGREEN, Colors.RED, Colors.ENDC, Colors.ENDC],
                         ['#', '#', '.', " "],
                         [cur, last_turn-cur, base-last_turn, max_pos-base])

def disp_hrule():
  return("="*80)

######
# IO #
######  
  
PAUSE_STRS = {
  "MORE_STR": Colors.INVERT + "MORE... [hit a key]" + Colors.ENDC,
  "FORMATION_STR": Style.BRIGHT + Back.WHITE + Fore.BLACK +  "Input " + Fore.BLUE + Back.BLACK +  "FORMATION" + Fore.BLACK + Back.WHITE + " for army {}$[7$] " + "({}):".format("/".join([rps.formation_info(i, "short") for i in ("O", "D")])) + Colors.ENDC,
  "ORDER_STR": Style.BRIGHT + Back.WHITE + Fore.BLACK +  "Input " + Fore.CYAN +  Back.BLACK + "ORDERS" + Fore.BLACK + Back.WHITE + " for army {} $[7$] " + "({}):".format("$[7$]/".join([rps.order_info(i,"short") for i in ("A", "D", "I")])) + Colors.ENDC
}

class BattleScreen():
  
  def __init__(self, battle):
    self.console_buf = []
    self.max_screen_len = 24
    self.max_stat_len = 2
    self.max_armies_len = 18
    self.max_console_len = 3
    self.max_footer_len = 1
    self.battle = battle 
    # self.screen = None # needs one

  def _colored_strats(self, orders):
    orders = list(orders)
    ocolors = []
    for i in [0,1]:
      other = 1-i
      if rps.beats(orders[i], orders[other]):
        ocolors.append(Colors.WIN)
      elif rps.beats(orders[other], orders[i]):
        ocolors.append(Colors.LOSE)
      else:
        ocolors.append("")
    return tuple([ocolors[i] + orders[i] + Colors.ENDC for i in [0,1]])
    
  def _day_status_str(self):
    """ what to put on top"""
    return "Day {}: {}".format(self.battle.date, self.battle.weather)

  def _vs_str(self):
    if self.battle.formations: # formation orders were given
      form0 = disp_form_short(self.battle.formations[0])
      form1 = disp_form_short(self.battle.formations[1])
    else:
      form0 = form1 = "?"
    if self.battle.orders:
    # if len(self.battle.order_history) == self.battle.date: # orders were given
      # strat0, strat1 = self._colored_strats(tuple(self.battle.order_history[-1]))
      strat0, strat1 = tuple(self.battle.order_history[-1])
      strat0 = disp_order_short(strat0)
      strat1 = disp_order_short(strat1)      
    else:
      strat0 = strat1 = "?"
    return "               ({}) {} -> {} VS {} <- {} ({})".format(disp_army(self.battle.armies[0]),
                                                     form0,
                                                     strat0,
                                                     strat1,
                                                     form1,
                                                     disp_army(self.battle.armies[1]))
  
  def _disp_statline(self):
    statline = self._day_status_str()
    return [statline, disp_hrule()]

  def _disp_armies(self): # 18 lines
    battle = self.battle
    armies_buf = []
      
    for j in [0,1]:
      for i in range(4):
        if len(battle.armies[j].present_units()) > i:
          unit = battle.armies[j].present_units()[i]
          header = self._disp_unit_newheader(unit, j)
          situ = self._disp_unit_newsitu(unit, j)
        else:
          header = ""
          situ = ""
        armies_buf.append(header)
        armies_buf.append(situ)
      if j == 0:
        # armies_buf.append(" "*39 + "VS" + " "*39)
        armies_buf.append(self._vs_str())
    armies_buf.append(disp_hrule())
    return armies_buf

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

  def _prerender(self, line):
    """ 
    converts a my-type color string to something on the screen

    1) I start with strings of the type ah$[3$]hhh$[7$], 
    2) which should become ah${3}hhh${7}, (this can be used by asciimatics)
    3) which in the final output should be converted to colorama (or some other 
    """
    return line.replace('$[', '${').replace('$]', '}')

  def _render(self, line):
    """
    converts a line of my-type of string (see prerender) to step 2, which is colorama-printable
    """
    return colors.str_to_colorama(self._prerender(line))
            
  def blit_all_battle(self, pause_str=None):
    # blits status
    self.disp_clear()
    st = self._disp_statline() # 2 lines
    ar = self._disp_armies() # 18 lines
    co = self._disp_console() # 3 lines
    fo = self._disp_footerline(pause_str) # 1 line, string
    assert len(st + ar + co) == self.max_screen_len - 1
    # effects = []
    for y, l in enumerate(st + ar + co):
      print(self._render(l))
    print(self._render(fo), end="", flush=True)
    #  effects.append(Print(self.screen, StaticRenderer(images=self._render(l)), x=0, y=y, colour=7))
    # screen.play([Scene(effects, -1)])
    self.console_buf = []
    return read_single_keypress()[0]
  
  def disp_damage(self, max_pos, oldsize, damage, dmgdata, dmglog):
    newsize = oldsize - damage
    hpbar = disp_bar_single_hit(20, oldsize, newsize)
    if not dmgdata:
      ndmgstr += " "
    elif dmgdata[0]: # this means there is a source; janky
      ndmgstr = "{} {} {} ".format(disp_unit(dmgdata[0]), dmgdata[2], disp_unit(dmgdata[1]))
    else:
      # this means a single target: "I got burned"
      ndmgstr = "{} is {} ".format(disp_unit(dmgdata[1]), dmgdata[2])
    fdmgstr = ndmgstr + hpbar + " {} -> {} ({} damage)".format(
      oldsize, newsize, colors.color_damage(damage))
    if newsize == 0:
      fdmgstr += "; " + Colors.RED + "DESTROYED!" + Colors.ENDC
    self.yprint(fdmgstr)
    if dmglog:
      dmg_str = disp_damage_calc(*dmglog)
      self.yprint(dmglog, debug=True)
    
  def _disp_unit_newheader(self, unit, side):
    healthbar = disp_bar_day_tracker(20, unit.size_base, unit.last_turn_size, unit.size)
    charstr = "{} {} Hp:{} Sp:{}".format(healthbar, disp_unit(unit), disp_unit_size(unit), unit.speed)
    if side == 0:
      return charstr
    else:
      return " "*0 + charstr

  def _disp_unit_newsitu(self, unit, side):
    charstr = " "*21
    statuses = disp_unit_status_noskills(unit)
    if statuses:
      charstr += "(" + statuses + "|"
    else:
      charstr += "("
    charstr += " ".join((s.short() for s in unit.character.skills)) + ")"
    if side == 0:
      # eventually may want to print differently based on which side they are on
      return charstr
    else:
      return " "*0 + charstr
    
  def disp_clear(self):
    os.system('cls' if os.name == 'nt' else 'clear')

  def _get_input(self, pause_str, accepted_inputs):
    # return input(prompt)
    while(True):
      pause_str = pause_str
      inp = self.blit_all_battle(pause_str=pause_str)
      if inp.upper() in accepted_inputs:
        return inp.upper()          
    
    
  def input_battle_formation(self, armyid):
    return self._get_input(PAUSE_STRS['FORMATION_STR'].format(armyid), ['O','D'])

  def input_battle_order(self, armyid):
    return self._get_input(PAUSE_STRS['ORDER_STR'].format(armyid), ['O','D'])

  def make_speech(self, unit, speech):
    """ What to display when a unit says something """
    self.yprint("{}: {}".format(disp_unit(unit), speech))

  def make_skill_narration(self, skill_str, other_str, success=None):
    """ What to display when we want to make a narration involving a skill """
    if success:
      successtr = "SUCCESS!"
    else:
      successtr = "FAIL!"
    if other_str == "":
      other_str = colors.color_bool(success) + successtr + Colors.ENDC
    self.yprint(disp_skill_activation(skill_str, success) + " " + other_str)
    
  def pause_and_display(self, pause_str=None):
    _ = self.blit_all_battle(pause_str=pause_str)

  def print_line(self, text):
    assert len(self.console_buf) <= self.max_console_len
    self.console_buf.append(text)
    if len(self.console_buf) == self.max_console_len:
      # just filled
      self.pause_and_display(pause_str=PAUSE_STRS["MORE_STR"])
    logging.info(text)

  def yprint(self, text, debug=False):
    logging.debug(text) # always log this
    if debug and not self.battle.debug_mode:
      return
    # so we get here if either SHOW_DEBUG or debug=False, which means we send it to the buffer
    self.print_line(text)
	  
  def yprint_hrule(self, debug=False):
    self.yprint(disp_hrule(), debug)

# import pygcurse
# win = pygcurse.PygcurseWindow(40, 25, 'Fall of the Dragon')
# print = win.pygprint
# input = win.input
# win.setscreencolors('lime', 'black', clear=True)

