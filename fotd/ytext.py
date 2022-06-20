"""
The overall idea is that all text data in this game is carried in my slightly
modified version of asciimatics text, YText. At the last second, it can be rendered 
to Colorama, asciimatics, or graphical views (in the future).

The second part really should be separated from this; it is more of a view for the battle than
a text utility module.
"""

import re
import colors

class YText():
  """

  Example YText(): 
  - initialize: 'Whoa$[3,1]$, this is $[4]$ color-coded text!' 
  - rendered (kept internally): 'Whoa${3,1}, this is ${4}color-coded text!'

  This scheme emulates asciimatics.renderer.
  """
 
  _colour_esc_code = r"^\$\{((\d+),(\d+),(\d+)|(\d+),(\d+)|(\d+))\}(.*)"
  _colour_sequence = re.compile(_colour_esc_code)

  def __init__(self, _str):
    """   
    Example of _str: $[4,1]$I am colored text$[7]$. 
    """
    self._str = self._prerender(_str)
    self.raw_str, self._color_map = self._to_asciimatics()
    self.pcolor_map = self._colormap_pygame(self._color_map)
    
  def _prerender(self, _str):
    """
    converts a my-type color string to something on the screen

    1) I start with strings of the type ah$[3]$hhh$[7]$, 
    2) which should become ah${3}hhh${7}, (this can be used by asciimatics)
    3) which in the final output should be converted to colorama (or some other 
    """
    return _str.replace('$[', '${').replace(']$', '}')

  def __len__(self):
    assert len(self.raw_str) == len(self._color_map)
    return len(self.raw_str)
  
  def _to_asciimatics(self):
    """
    asciimatics paints with a raw (straight text) 'image' and a color map of 3-tuples of attributes
    which it then gives to Renderers / the paint() function. 

    This converts a YText instance to such a thing, which we then either
    - render in the stdio / default, or
    - TODO: render in asciimatics screens

    color map format: (foreground, attribute, background). See colors.

    This means the first element is the color, the second, if it is there, is the foreground.
    Finally, we might have an attribute (which we can ignore for now))
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

  def _colormap_pygame(self, color_map):
    """
    Convert colors to pygame style
    """
    cm = []
    for a, c, b in color_map:
      # ignore attributes for now
      if a == None:
        a = 8
      if b == None:
        b = 0
      cm.append((colors.PCOLOR_FROM_ASCIIMATICS[a],
                 colors.PCOLOR_FROM_ASCIIMATICS[b],
                 c))
    return cm


def disp_text_activation(any_str, success=None, upper=True):
  """
  to display an ``activated'' string (skill, skillcard, whatever) to give a decorated 
  context.
  """
  if upper:
    newstr = any_str.upper()
  else:
    newstr = any_str
  # return "<" + colors.color_bool(success) + " ".join(newstr.split("_")) + "$[7]$>"
  return "<" + colors.color_bool(success) + " ".join(newstr.split("_")) + "$[7]$>"



