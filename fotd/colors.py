from colorama import Fore, Back, Style, init
init()

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
  INVERT = Fore.BLACK + Back.WHITE

# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL
  
# ESC [ 0 m       # reset all (colors and brightness)
# ESC [ 1 m       # bright
# ESC [ 2 m       # dim (looks same as normal brightness)
# ESC [ 22 m      # normal brightness

# # FOREGROUND:
# ESC [ 30 m      # black
# ESC [ 31 m      # red
# ESC [ 32 m      # green
# ESC [ 33 m      # yellow
# ESC [ 34 m      # blue
# ESC [ 35 m      # magenta
# ESC [ 36 m      # cyan
# ESC [ 37 m      # white
# ESC [ 39 m      # reset

# # BACKGROUND
# ESC [ 40 m      # black
# ESC [ 41 m      # red
# ESC [ 42 m      # green
# ESC [ 43 m      # yellow
# ESC [ 44 m      # blue
# ESC [ 45 m      # magenta
# ESC [ 46 m      # cyan
# ESC [ 47 m      # white
# ESC [ 49 m      # reset

# # cursor positioning
# ESC [ y;x H     # position cursor at x across, y down
# ESC [ y;x f     # position cursor at x across, y down
# ESC [ n A       # move cursor n lines up
# ESC [ n B       # move cursor n lines down
# ESC [ n C       # move cursor n characters forward
# ESC [ n D       # move cursor n characters backward

# # clear the screen
# ESC [ mode J    # clear the screen

# # clear the line
# ESC [ mode K    # clear the line
     
class Colours:
  # for asciimatics
  BLACK = 0
  RED = 1
  GREEN = 2
  YELLOW = 3
  BLUE = 4
  MAGENTA = 5
  CYAN = 6
  WHITE = 7

class Attrs:
  # for asciimatics
  A_BOLD = 1
  A_NORMAL = 2
  A_REVERSE = 3
  A_UNDERLINE = 4
  


# Takes something like "${5} Yan Zhang ${7}" and converts it to Colorama codes so we can just 
STR_TO_CR = {
  "${1}":Colors.RED,
  "${2}":Colors.GREEN,
  "${3}":Colors.YELLOW,
  "${4}":Colors.BLUE,
  "${5}":Colors.MAGENTA,
  "${6}":Colors.CYAN,
  "${7}":Colors.ENDC,
  "${2,1}":Colors.GREEN + Style.BRIGHT,
  "${1,3}":Back.RED + Fore.WHITE,
  "${7,1}":Fore.WHITE + Style.BRIGHT
}

def ctext(text, colornumstr):
  return("$[{}]$".format(colornumstr) + text + "$[7]$")

def str_to_colorama(my_str):
  new_str = my_str
  for k in STR_TO_CR:
    new_str = new_str.replace(k, STR_TO_CR[k])
  return new_str

# color functions

def color_bool(success):
  if success:
    return Colors.OKGREEN
  elif success == False:
    return Colors.MAGENTA
  else:
    # when we don't know if it failed
    return Colors.GREEN

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

def color_size(size, size_base):
  if size >= 0.66*size_base:
    return Colors.OKGREEN
  elif size >= 0.33*size_base:
    return Colors.YELLOW
  else:
    return Colors.RED
