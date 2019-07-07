import sys
import logging
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

SCROLL_COUNT = 0
MAX_SCROLL_COUNT = 24

MORE_STR = Fore.BLACK + Back.WHITE + "MORE... [hit a key]" + Colors.ENDC  

def yinput(prompt):
  global SCROLL_COUNT
  SCROLL_COUNT = 0
  # return input(prompt)
  inp = ' '
  while(inp.upper() not in ['A', 'D', 'I']):
    yprint(Fore.BLACK + Back.WHITE + prompt + Colors.ENDC)
    inp = read_single_keypress()[0]
  SCROLL_COUNT = 0
  return inp

def yprint(text, debug=False):
  global SHOW_DEBUG
  logging.debug(text) # always log this
  if debug and not SHOW_DEBUG:
    return
  # so we get here if either SHOW_DEBUG or debug=False
  global SCROLL_COUNT
  if SCROLL_COUNT == MAX_SCROLL_COUNT:
    logging.info(MORE_STR)
    read_single_keypress()
    SCROLL_COUNT = 0
  print(text)
  SCROLL_COUNT += 1
  
def pause(clear=False):
  print(MORE_STR)
  read_single_keypress()
  global SCROLL_COUNT
  SCROLL_COUNT = 0
  if clear:
    os.system('cls' if os.name == 'nt' else 'clear')
  
def disp_bar(total, base, cur):
  """Total: length; base: max; cur: current. """
  return  Colors.OKGREEN + '#'*cur + Colors.RED + '#'*(base-cur) + Colors.ENDC + '.'*(total-base)

def yprint_hrule(debug=False):
  yprint("===========================================================", debug)
# import pygcurse
# win = pygcurse.PygcurseWindow(40, 25, 'Fall of the Dragon')
# print = win.pygprint
# input = win.input
# win.setscreencolors('lime', 'black', clear=True)

