# import graphics_asciimatics
from utils import read_single_keypress
import os
import logging
import colors
from colors import Colors, Colours, Fore, Back, Style

import sys
import rps

######################
# Formatting Strings #
######################
  
def damage_str(s_str, d_str, dicecount, hitprob, raw_damage):
  return "[Strength: ({:4.3f} vs. {:4.3f}); {} dice with chance {} each; Final: {}]".format(
    s_str, d_str, dicecount, colors.color_prob(hitprob), colors.color_damage(raw_damage))

######
# Display (convert to string) Functions #
######

def disp_army(army):
  return "$[{}$]{}$[7$]".format(army.color, army.name)

def disp_unit(unit):
  return "$[{}$]{}$[7$]".format(unit.color, unit.name)

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
  
MORE_STR = Colors.INVERT + "MORE... [hit a key]" + Colors.ENDC  

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
    if self.battle.formations[0] == None:
      form0 = form1 = "?"
    else:
      form0 = self.battle.formations[0]
      form1 = self.battle.formations[1]
    if len(self.battle.order_history) == self.battle.date: # orders were given
      strat0, strat1 = self._colored_strats(tuple(self.battle.order_history[-1]))
    else:
      strat0 = strat1 = "?"
    return "Day {}: ({}) {} -> {} vs {} <- {} ({})".format(self.battle.date,
                                                           disp_army(self.battle.armies[0]),
                                                           form0,
                                                           strat0,
                                                           strat1,
                                                           form1,
                                                           disp_army(self.battle.armies[1]),
                                                           str(self.battle.weather)) 

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
        armies_buf.append(" "*39 + "VS" + " "*39)
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
    converts a my-type color string to one that can be rendered.

    I'm going to end up with strings of the type ah[3]hhh[7], which should become ah${3}hhh${7},
    which in the final print should be converted to colorama (or some other output)

    """
    return line.replace('$[', '${').replace('$]', '}')
            
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
      print(colors.str_to_colorama(self._prerender(l)))
    print(fo, end="", flush=True)
    #  effects.append(Print(self.screen, StaticRenderer(images=self._render(l)), x=0, y=y, colour=7))
    # screen.play([Scene(effects, -1)])
    self.console_buf = []
    return read_single_keypress()[0]

  def disp_damage(self, max_pos, oldsize, damage, dmgstr, dmglog):
    newsize = oldsize - damage
    hpbar = disp_bar_single_hit(20, oldsize, newsize)
    ndmgstr = dmgstr
    if ndmgstr:
      ndmgstr += " "
    fdmgstr = ndmgstr + hpbar + " {} -> {} ({} damage)".format(
      oldsize, newsize, colors.color_damage(damage))
    if newsize == 0:
      fdmgstr += "; " + Colors.RED + "DESTROYED!" + Colors.ENDC
    self.yprint(fdmgstr)
    if dmglog:
      dmg_str = damage_str(*dmglog)
      self.yprint(dmglog, debug=True)
    
  def _disp_unit_newheader(self, unit, side):
    healthbar = disp_bar_day_tracker(20, unit.size_base, unit.last_turn_size, unit.size)
    charstr = "{} {} Hp:{} Sp:{}".format(healthbar, disp_unit(unit), unit.size_repr(), unit.speed)
    if side == 0:
      return charstr
    else:
      return " "*0 + charstr

  def _disp_unit_newsitu(self, unit, side):
    charstr = " "*21
    statuses = unit.status_real_repr()
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

  def input_battle_formation(self, armyid):
    # return input(prompt)
    while(True):
      pause_str = Style.BRIGHT + Back.WHITE + Fore.BLACK +  "Input " + Fore.BLUE + Back.BLACK +  "FORMATION" + Fore.BLACK + Back.WHITE + " for army {} ".format(armyid) +  Fore.BLUE + Back.BLACK + "(O/D):" + Colors.ENDC
      inp = self.blit_all_battle(pause_str=pause_str)
      if inp.upper() in ['O', 'D']:
        return inp.upper()          

  def input_battle_order(self, armyid):
    # return input(prompt)
    while(True):
      pause_str = Style.BRIGHT + Back.WHITE + Fore.BLACK +  "Input " + Fore.CYAN +  Back.BLACK + "ORDERS" + Fore.BLACK + Back.WHITE + " for army {}".format(armyid) + Fore.CYAN + Back.BLACK + " (A/D/I):" +  Colors.ENDC
      inp = self.blit_all_battle(pause_str=pause_str)
      if inp.upper() in ['A', 'D', 'I']:
        return inp.upper()      
    
  def pause_and_display(self, pause_str=None):
    _ = self.blit_all_battle(pause_str=pause_str)

  def print_line(self, text):
    assert len(self.console_buf) <= self.max_console_len
    self.console_buf.append(text)
    if len(self.console_buf) == self.max_console_len:
      # just filled
      self.pause_and_display(pause_str=MORE_STR)
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

