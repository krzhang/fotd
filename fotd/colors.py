from colorama import Fore, Back, Style, init
init()

class Colors:
  # HEADER = '\033[95m'
  # OKBLUE = '\033[94m'
  # OKGREEN = '\033[92m'
  # WARNING = '\033[93m'
  # FAIL = '\033[91m'
  # # ENDC = '\033[0m'
  ENDC = Style.RESET_ALL
  # BOLD = '\033[1m'
  UNDERLINE = '\033[4m'
  # mine below
  # BLACK
  RED = "$[1]$"
  GREEN = "$[2]$"
  YELLOW = "$[3]$"
  BLUE = "$[4]$"
  MAGENTA = "$[5]$"
  CYAN = "$[6]$"
  WHITE = "$[7]$"
  # BLUE = Fore.BLUE
  # YELLOW = Fore.YELLOW
  # RED = Fore.RED
  # GREEN = Fore.GREEN
  # MAGENTA = Fore.MAGENTA
  # CYAN = Fore.CYAN
  # RPS
  # By function
  INVERT = "$[0,3,7]$"
  SUCCESS = "$[2,1]$"
  GOOD = "$[2]$"
  NEUTRAL = "$[5]$"
  POOR = "$[3]$"
  FAILURE = "$[1]$"

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

  
def ctext(text, colornumstr):
  return(colornumstr + text + "$[7]$")

# color functions
  
def color_bool(success):
  if success:
    return Colors.SUCCESS
  elif success == False:
    return Colors.FAILURE
  else:
    # when we don't know if it failed
    return Colors.NEUTRAL

def color_prob(prob):
  pstr = "{:4.3f}".format(prob)
  if prob > 0.8:
    return ctext(pstr, Colors.SUCCESS)
  elif prob > 0.6:
    return ctext(pstr, Colors.GOOD)
  elif prob > 0.4:
    return ctext(pstr, Colors.NEUTRAL)
  elif prob > 0.2:
    return ctext(pstr, Colors.POOR)
  else:
    return ctext(pstr, Colors.FAILURE)

def color_damage(damage):
  if damage == 0:
    return ctext(str(damage), Colors.SUCCESS)
  elif damage <= 3:
    return ctext(str(damage), Colors.NEUTRAL)
  else:
    return ctext(str(damage), Colors.FAILURE)

def color_size(size, size_base):
  return color_prob(float(size)/size_base)
