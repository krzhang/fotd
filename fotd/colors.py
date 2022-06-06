from pygame import Color

class PColors:
  # colors from Pygame
  BLACK  = Color(0, 0, 0)
  RED    = Color(255, 0, 0)
  GREEN  = Color(0, 255, 0)
  YELLOW = Color(255, 255, 0)
  BLUE   = Color(0, 0, 255)
  MAGENTA = Color(255, 0, 255)
  CYAN = Color (0, 255, 255)
  WHITE  = Color(255, 255, 255)
  GREY   = Color(160, 160, 160)
  ICE    = Color(92, 247, 251)
   
  GREEN_A50  = Color(0, 255, 0, 50)
  RED_A50    = Color(255, 0, 0, 50)
  BLUE_A50   = Color(0, 0, 255, 50)
  YELLOW_A50 = Color(255, 200, 0, 50)
  GREY_A50   = Color(160, 160, 160, 50)
  GREY_A200  = Color(100, 100, 100, 200)

  highlight = {
    'selected': Color(255, 200, 0, 100),
    'move': Color(0, 0, 255, 75),
    'attack': Color(255, 0, 0, 75),
    'played': Color(75, 75, 75, 150),
  }

  MENU_SEL = Color(96, 144, 145)
  MENU_BG  = Color(51, 51, 51)

  TRANSPARENT = Color(0, 0, 0, 0)

# quick numerical conversion from ASCIIMATICS numbers to Pygame colors
PCOLOR_FROM_ASCIIMATICS = {
  0:PColors.BLACK,
  1:PColors.RED,
  2:PColors.GREEN,
  3:PColors.YELLOW,
  4:PColors.BLUE,
  5:PColors.MAGENTA,
  6:PColors.CYAN,
  7:PColors.WHITE,
  8:PColors.GREY}

class YCodes:
  """ Codes for YText objects"""
  # mine below
  BLACK = "$[0]$"
  RED = "$[1]$"
  GREEN = "$[2]$"
  YELLOW = "$[3]$"
  BLUE = "$[4]$"
  MAGENTA = "$[5]$"
  CYAN = "$[6]$"
  WHITE = "$[7]$"
  GREY = "$[8]$"
  # by functionality
  INVERT = "$[7,3]$"
  SUCCESS = "$[2,1]$"
  GOOD = "$[2]$"
  NEUTRAL = "$[5]$"
  POOR = "$[3]$"
  FAILURE = "$[1]$"
  
def ctext(text, colornumstr):
  return(colornumstr + text + "$[8]$")

# color functions
  
def color_bool(success):
  if success:
    return YCodes.SUCCESS
  elif success == False:
    return YCodes.FAILURE
  else:
    # when we don't know if it failed
    return YCodes.NEUTRAL

def color_prob(prob):
  pstr = "{:4.3f}".format(prob)
  if prob > 0.8:
    return ctext(pstr, YCodes.SUCCESS)
  elif prob > 0.6:
    return ctext(pstr, YCodes.GOOD)
  elif prob > 0.4:
    return ctext(pstr, YCodes.NEUTRAL)
  elif prob > 0.2:
    return ctext(pstr, YCodes.POOR)
  else:
    return ctext(pstr, YCodes.FAILURE)

def color_damage(damage):
  if damage == 0:
    return ctext(str(damage), YCodes.SUCCESS)
  elif damage <= 3:
    return ctext(str(damage), YCodes.NEUTRAL)
  else:
    return ctext(str(damage), YCodes.FAILURE)

def color_size(size, size_base):
  return color_prob(float(size)/size_base)
