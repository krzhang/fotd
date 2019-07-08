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

from colorama import Fore, Back, Style
from utils import read_single_keypress
import os

class Colors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  # ENDC = '\033[0m'
  ENDC = Style.RESET_ALL
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'
  # mine below
  BLUE = Fore.BLUE
  YELLOW = Fore.YELLOW
  RED = Fore.RED
  GREEN = Fore.GREEN
  MAGENTA = Fore.MAGENTA
  CYAN = Fore.CYAN
  # RPS
  WIN = OKGREEN
  LOSE = Fore.RED

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


######
# IO #
######
  
MORE_STR = Fore.BLACK + Back.WHITE + "MORE... [hit a key]" + Colors.ENDC  


class BattleScreen():
  def __init__(self):
    self.console_buf = []
    self.max_screen_len = 24
    self.max_stat_len = 3
    self.max_armies_len = 20
    self.max_console_len = 5
    self.battle = None # needs one eventually

  def _colored_strats(self, orders):
    orders = list(orders)
    colors = []
    for i in [0,1]:
      other = 1-i
      if rps.beats(orders[i], orders[other]):
        colors.append(Colors.WIN)
      elif rps.beats(orders[other], orders[i]):
        colors.append(Colors.LOSE)
      else:
        colors.append("")
    return tuple([colors[i] + orders[i] + Colors.ENDC for i in [0,1]])
    
    
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
    
  def blit_all_battle(self):
    # blits status
    self.disp_clear()
    print(disp_hrule()) # 1 line
    print(self._day_status_str())
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
        print(situ)
        print(header)
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
      print(i)
      
  def disp_unit_header(self, unit, side):
    """ Ex: ################.... 7/16 Sp:12 """
    char1 = "{} ".format(repr(unit))
    char2 = "{}".format(" ".join((s.short() for s in unit.character.skills)))
    if side == 0:
      # eventually may want to print differently based on which side they are on
      return char1 + char2
    else:
      return " "*0 + char1 + char2
    
  def disp_unit_newheader(self, unit, side):
    healthbar = disp_bar(20, unit.size_base, unit.size)
    charstr = "{} {} Hp:{} Sp:{}".format(healthbar, repr(unit), unit.size_repr(), unit.speed)
    if side == 0:
      return charstr
    else:
      return " "*0 + charstr

  def disp_unit_situ(self, unit, side):
    """ Ex: Albert Einstein -=Eureka=- <c-k-n> """
    healthbar = disp_bar(20, unit.size_base, unit.size)
    charstr = "{} {} Sp:{} {}".format(healthbar, unit.size_repr(), unit.speed, unit.status_real_repr())
    if side == 0:
      return charstr
    else:
      return " "*0 + charstr

  def disp_unit_newsitu(self, unit, side):
    charstr = "{} {}".format(unit.status_real_repr(),
                             " ".join((s.short() for s in unit.character.skills)))
    if side == 0:
      # eventually may want to print differently based on which side they are on
      return charstr
    else:
      return " "*0 + charstr

    
  def disp_clear(self):
    os.system('cls' if os.name == 'nt' else 'clear')
    
  def pause_and_display(self):
    self.blit_all_battle()
    read_single_keypress()
    self.console_buf = []

  def print_line(self, text):
    if len(self.console_buf) == self.max_console_len:
      self.console_buf.append(MORE_STR)
      self.pause_and_display()
    logging.info(text)
    self.console_buf.append(text)

BATTLE_SCREEN = BattleScreen()
    
def yinput_battle_order(prompt):
  # return input(prompt)
  while(True):
    BATTLE_SCREEN.console_buf = []
    BATTLE_SCREEN.blit_all_battle()
    print(prompt)
    inp = read_single_keypress()[0]
    if inp.upper() in ['A', 'D', 'I']:
      return inp.upper()
      

def yprint(text, debug=False):
  global SHOW_DEBUG
  logging.debug(text) # always log this
  if debug and not SHOW_DEBUG:
    return
  # so we get here if either SHOW_DEBUG or debug=False, which means we send it to the buffer
  BATTLE_SCREEN.print_line(text)
  
  
def disp_bar(total, base, cur):
  """Total: length; base: max; cur: current. """
  return  Colors.OKGREEN + '#'*cur + Colors.RED + '#'*(base-cur) + Colors.ENDC + '.'*(total-base)

def disp_hrule():
  return("="*80)

def yprint_hrule(debug=False):
  yprint(disp_hrule(), debug)
# import pygcurse
# win = pygcurse.PygcurseWindow(40, 25, 'Fall of the Dragon')
# print = win.pygprint
# input = win.input
# win.setscreencolors('lime', 'black', clear=True)

