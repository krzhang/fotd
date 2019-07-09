import graphics
import sys
import logging
import rps

# create logger with 'spam_application'
logger = logging.getLogger("test")
logger.setLevel(logging.DEBUG)

f = logging.FileHandler("test.log")
f.setLevel(logging.DEBUG)
logger.addHandler(f)

# handler = logging.StreamHandler(sys.stdout)
# handler.setLevel(logging.DEBUG)
# logger.addHandler(handler)

SHOW_DEBUG = False

from utils import read_single_keypress
import os
import colors
from colors import Colors

######################
# Formatting Strings #
######################

def color_prob(prob):
  pstr = "{:4.3f}".format(prob)
  if prob > 0.75:
    return Colors.GREEN + pstr + Colors.ENDC
  elif prob > 0.5:
    return Colors.MAGENTA + pstr + Colors.ENDC
  elif prob > 0.25:
    return Colors.YELLOW + pstr + Colors.ENDC
  else:
    return Colors.RED + pstr + Colors.ENDC
  
def color_damage(damage):
  if damage == 0:
    return Colors.OKGREEN + str(damage) + Colors.ENDC
  elif damage <= 3:
    return str(damage)
  else:
    return Colors.RED + str(damage) + Colors.ENDC

def damage_str(s_str, d_str, dicecount, hitprob, raw_damage):
  return "[Strength: ({:4.3f} vs. {:4.3f}); {} dice with chance {} each; Final: {}]".format(
    s_str, d_str, dicecount, color_prob(hitprob), color_damage(raw_damage))

######
# IO #
######
  
MORE_STR = Colors.INVERT + "MORE... [hit a key]" + Colors.ENDC  

class BattleScreen():
  def __init__(self, battle):
    self.console_buf = []
    self.max_screen_len = 24
    self.max_stat_len = 3
    self.max_armies_len = 20
    self.max_console_len = 4
    self.battle = battle # needs one eventually
    # self.screen = graphics.Screen.wrapper(graphics.battle_screen)

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
    if len(self.battle.order_history) == self.battle.date: # orders were given
      strat1, strat2 = self._colored_strats(tuple(self.battle.order_history[-1]))
    else:
      strat1 = strat2 = "?"
    return "Day {}: ({}) {} vs {} ({}) {}".format(self.battle.date,
                                                  self.battle.armies[0].name,
                                                  strat1,
                                                  strat2,
                                                  self.battle.armies[1].name,
                                                  str(self.battle.weather)) 

  
  
  def blit_all_battle(self, pause_str=None):
    # blits status
    self.disp_clear()
    print(disp_hrule()) # 1 line
    statline = self._day_status_str()
    print(statline)
    print(disp_hrule()) # 3 line
    # armies
    battle = self.battle
    armies_buf = []
    disp1 = {0:None, 1:None}
    disp2 = {0:None, 1:None}

    # for i in range(5):
    #   for j in [0,1]:
    #     if len(battle.armies[j].present_units()) > i:
    #       disp1[j] = self.disp_unit_header(battle.armies[j].present_units()[i], j)
    #       disp2[j] = self.disp_unit_situ(battle.armies[j].present_units()[i], j)
    #     else:
    #       disp1[j] = " "*40
    #       disp2[j] = " "*40
      
    for j in [0,1]:
      for unit in battle.armies[j].present_units():
        header = self.disp_unit_newheader(unit, j)
        situ = self.disp_unit_newsitu(unit, j)
        print(header)
        print(situ)
      if j == 0:
        print(" "*39 + "VS" + " "*39)
          
    # # blits console
    # for i in range(self.max_console_len): # 11
    #   if len(self.console_buf) > i:
    #     print(self.console_buf[i])
    #   else:
    #     print("")
    print(disp_hrule()) # 3 line      
    for i in self.console_buf:
      print(console_buf[i])

  def disp_damage(self, max_pos, oldsize, damage, dmgstr, dmglog):
    newsize = oldsize - damage
    hpbar = disp_bar_single_hit(20, oldsize, newsize)
    ndmgstr = dmgstr
    if ndmgstr:
      ndmgstr += " "
    fdmgstr = ndmgstr + hpbar + " {} -> {} ({} damage)".format(
      oldsize, newsize, color_damage(damage))
    if newsize == 0:
      fdmgstr += "; " + Colors.RED + "DESTROYED!" + Colors.ENDC
    self.yprint(fdmgstr)
    if dmglog:
      dmg_str = damage_str(*dmglog)
      self.yprint(dmglog, debug=True)
      
  def disp_unit_newheader(self, unit, side):
    healthbar = disp_bar_day_tracker(20, unit.size_base, unit.last_turn_size, unit.size)
    charstr = "{} {} Hp:{} Sp:{}".format(healthbar, repr(unit), unit.size_repr(), unit.speed)
    if side == 0:
      return charstr
    else:
      return " "*0 + charstr

  def disp_unit_newsitu(self, unit, side):
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

  def input_battle_order(self, armyid):
    # return input(prompt)
    while(True):
      self.console_buf = []
      self.blit_all_battle()
      print("Input orders for army {}(A/D/I):".format(armyid), end="", flush=True)
      inp = read_single_keypress()[0]
      if inp.upper() in ['A', 'D', 'I']:
        return inp.upper()      
    
  def pause_and_display(self, pause_str=None):
    self.blit_all_battle(, pause_str=pause_str)
    read_single_keypress()
    self.console_buf = []

  def print_line(self, text):
    if len(self.console_buf) == self.max_console_len-2:
      self.pause_and_display(pause_str=MORE_STR)
    logging.info(text)
    self.console_buf.append(text)

  def yprint(self, text, debug=False):
    global SHOW_DEBUG
    logging.debug(text) # always log this
    if debug and not SHOW_DEBUG:
      return
    # so we get here if either SHOW_DEBUG or debug=False, which means we send it to the buffer
    self.print_line(text)
	  
  def yprint_hrule(self, debug=False):
    self.yprint(disp_hrule(), debug)

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
  
# import pygcurse
# win = pygcurse.PygcurseWindow(40, 25, 'Fall of the Dragon')
# print = win.pygprint
# input = win.input
# win.setscreencolors('lime', 'black', clear=True)

