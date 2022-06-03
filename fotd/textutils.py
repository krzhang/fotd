"""
The overall idea is that all text data in this game is carried in my slightly
modified version of asciimatics text, YText. At the last second, it can be rendered 
to Colorama, asciimatics, or graphical views (in the future).

The second part really should be separated from this; it is more of a view for the battle than
a text utility module.
"""

import re

# import graphics_asciimatics
import colors
from colors import ctext, Colors, Fore, Back, Style

AM_TO_CR_FORE = {
  0:Fore.BLACK,
  1:Fore.RED,
  2:Fore.GREEN,
  3:Fore.YELLOW,
  4:Fore.BLUE,
  5:Fore.MAGENTA,
  6:Fore.CYAN,
  7:Fore.WHITE,  
}

AM_TO_CR_BACK = {
  0:Back.BLACK,
  1:Back.RED,
  2:Back.GREEN,
  3:Back.YELLOW,
  4:Back.BLUE,
  5:Back.MAGENTA,
  6:Back.CYAN,
  7:Back.WHITE,  
}

ATTRIBUTES = {
    "1": 1, # BOLD
    "2": 2, # NORMAL
    "3": 3, # REVERSE
    "4": 4, # UNDERLINE
}

class YText():
  """
  Example: Zhang Fei: $[4,1]$I am colored text$[7]$.

  Much of this code is taken from asciimatics.renderer, converted for my purposes  
  """

  _colour_esc_code = r"^\$\{((\d+),(\d+),(\d+)|(\d+),(\d+)|(\d+))\}(.*)"
  _colour_sequence = re.compile(_colour_esc_code)

  def __init__(self, _str):
    self._str = self._prerender(_str)
    self._raw_str, self._color_map = self._to_asciimatics()

  def _prerender(self, _str):
    """
    converts a my-type color string to something on the screen

    1) I start with strings of the type ah$[3]$hhh$[7]$, 
    2) which should become ah${3}hhh${7}, (this can be used by asciimatics)
    3) which in the final output should be converted to colorama (or some other 
    """
    return _str.replace('$[', '${').replace(']$', '}')

  def __len__(self):
    assert len(self._raw_str) == len(self._color_map)
    return len(self._raw_str)
  
  def to_colorama_old(self):
    """
    colorama just prints strings with escape characters embedded in
    """
    new_str = self._str
    for k in STR_TO_CR:
      new_str = new_str.replace(k, STR_TO_CR[k])
    return new_str

  def to_colorama(self):
    """
    colorama just prints strings with escape characters embedded in
    """
    cur_map = (None, None, None)
    new_str = ""
    for i, t in enumerate(self._raw_str):
      if self._color_map[i] != cur_map:
        new_str += Colors.ENDC
        cur_map = self._color_map[i]
        a,b,c = self._color_map[i]
        assert a is not None
        if b == 1: # BOLD
          new_str += Style.BRIGHT
        elif b == 2: # NORMAL
          new_str += Style.NORMAL
        elif b == 4: # UNDERLINE
          new_str += Style.UNDERLINE
        elif b == 3: # REVERSE
          if c is None:
            c = 0
          a, c = c, a
        if c:
          new_str += AM_TO_CR_BACK[c]
        else:
          pass
        assert a is not None
        new_str += AM_TO_CR_FORE[a]
      new_str += t
    return new_str + Colors.ENDC

  def to_pygame(self):
    """
    For now, just return the raw text; we can convert the color stuff later
    """
    return self._raw_str
  
  def _to_asciimatics(self):
    """
    asciimatics paints with a raw (straight text) 'image' and a color map of 3-tuples of attributes
    which it then gives to Renderers / the paint() function. (never really figured this out, see
    samples)

    This converts a YText instance to such a thing, which we then either
    - render in the stdio / default, or
    - TODO: render in asciimatics screens
    """
    new_line = ""
    attributes = (None, None, None)
    colours = []
    line = self._str
    while len(line) > 0:
      match = self._colour_sequence.match(line)
      if match is None:
        new_line += line[0]
        colours.append(attributes)
        line = line[1:]
      else:
        # The regexp either matches:
        # - 2,3,4 for ${c,a,b}
        # - 5,6 for ${c,a}
        # - 7 for ${c}.
        if match.group(2) is not None:
          attributes = (int(match.group(2)),
                        int(match.group(3)),  # in asciimatics these are ATTRIBUTES
                        int(match.group(4)))
        elif match.group(5) is not None:
          attributes = (int(match.group(5)),
                        int(match.group(6)),
                        None)
        else:
          attributes = (int(match.group(7)), 0, None)
        line = match.group(8)
    return(new_line, colours)
  




