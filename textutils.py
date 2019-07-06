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
MAX_SCROLL_COUNT = 22

MORE_STR = Fore.BLACK + Back.WHITE + "MORE... [hit a key]" + Colors.ENDC  

def yinput(prompt):
  global SCROLL_COUNT
  SCROLL_COUNT = 0
  return input(prompt)

def yprint(text):
  global SCROLL_COUNT
  if SCROLL_COUNT == MAX_SCROLL_COUNT:
    print(MORE_STR)
    read_single_keypress()
    SCROLL_COUNT = 0
  print(text)
  SCROLL_COUNT += 1

def reset_buffer():
  print(MORE_STR)
  read_single_keypress()
  global SCROLL_COUNT
  SCROLL_COUNT = 0
  os.system('cls' if os.name == 'nt' else 'clear')


# import pygcurse
# win = pygcurse.PygcurseWindow(40, 25, 'Fall of the Dragon')
# print = win.pygprint
# input = win.input
# win.setscreencolors('lime', 'black', clear=True)

