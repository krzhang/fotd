from collections import defaultdict
import sys
import random

from pyfiglet import Figlet
from asciimatics.effects import Cycle, Print, Stars, Sprite, RandomNoise
from asciimatics.event import KeyboardEvent, MouseEvent
from asciimatics.exceptions import ResizeScreenError, StopApplication
from asciimatics.particles import Explosion, StarFirework, DropScreen, Rain
from asciimatics.paths import Path, DynamicPath
from asciimatics.renderers import StaticRenderer, SpeechBubble, FigletText, Rainbow
from asciimatics.renderers import SpeechBubble, FigletText, Box, Fire
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.widgets import Frame, Layout, MultiColumnListBox, Widget, Label, TextBox, PopUpDialog


class YTextBox(TextBox):
  def __init__(self, height, label=None, name=None, as_string=False, line_wrap=False,
           on_change=None, **kwargs):
    """
    :param height: The required number of input lines for this TextBox.
    :param label: An optional label for the widget.
    :param name: The name for the TextBox.
    :param as_string: Use string with newline separator instead of a list
    for the value of this widget.
    :param line_wrap: Whether to wrap at the end of the line.
    :param on_change: Optional function to call when text changes.
  
    Also see the common keyword arguments in :py:obj:`.Widget`.
    """
    super().__init__(name, **kwargs)
        
  def update(self, frame_no):
    self._draw_label()
    
    # Calculate new visible limits if needed.
    height = self._h
    if not self._line_wrap:
      self._start_column = min(self._start_column, self._column)
      # self._start_column += _find_min_start(
      #   self._value[self._line][self._start_column:self._column + 1],
      #   self.width,
      #   self._frame.canvas.unicode_aware,
      #   self._column >= self.string_len(self._value[self._line]))
    
    # Clear out the existing box content
    (colour, attr, bg) = self._pick_colours("edit_text")
    for i in range(height):
      self._frame.canvas.print_at(" " * self.width,
                                  self._x + self._offset,
                                  self._y + i,
                                  colour, attr, bg)
    
    # Convert value offset to display offsets
    # NOTE: _start_column is always in display coordinates.
    display_text = self._reflowed_text
    display_start_column = self._start_column
    display_line, display_column = 0, 0
    for i, (_, line, col) in enumerate(display_text):
      if line <= self._line and col <= self._column:
        display_line = i
        display_column = self._column - col
    
    # Restrict to visible/valid content.
    self._start_line = max(0, max(display_line - height + 1,
                              min(self._start_line, display_line)))
    
    image, colours = StaticRenderer(self.value).rendered_text
    for (i, line) in enumerate(image):
      self._frame.canvas.paint(line, self._x, self._y + i, self._colour,
                                   attr=self._attr,
                                   bg=self._bg,
                                   transparent=self._transparent,
                                   colour_map=colours[i])

class BattleFrame(Frame):
  def __init__(self, screen, battle):
    super().__init__(screen,
                     screen.height,
                     screen.width,
                     has_border=False)
    self.battle = battle
    layout = Layout([1], fill_frame=True)
    self.statline = YTextBox(2)
    self.statline.disabled = True
    self.armystats = YTextBox(18)
    self.armystats.disabled = True
    self.console = YTextBox(3)
    self.console.disabled = True
    self.add_layout(layout)
    layout.add_widget(self.statline)
    layout.add_widget(self.armystats)
    layout.add_widget(self.console)
    self.fix()
    self._canvas.clear_buffer(0, 0, 0)
    
  def _prerender(self, line):
    """ 
    converts a my-type color string to one that can be rendered.

    I'm going to end up with strings of the type ah[3]hhh[7], which should become ah${3}hhh${7}

    """
    return line.replace('$[', '${').replace('$]', '}')
    
  def reset(self):
    # Do standard reset to clear out form, then populate with new data.
    super().reset()
        
  def process_event(self, event):
    # Do the key handling for this Frame.
    if isinstance(event, KeyboardEvent):
      if event.key_code in [ord('q'), ord('Q'), Screen.ctrl("c")]:
        self._quit()
      elif event.key_code in [ord("r"), ord("R")]:

        self.statline.value = [self._prerender(l) for l in self.battle.battlescreen._disp_statline()]
        self.armystats.value = [self._prerender(l) for l in self.battle.battlescreen._disp_armies()]
        self.console.value = [self._prerender(l) for l in self.battle.battlescreen._disp_console()]
        
        self._last_frame = 0

    # Now pass on to lower levels for normal handling of the event.
    return super().process_event(event)
  
  def _quit(self):
    self._scene.add_effect(
      PopUpDialog(self._screen,
                  "Are you sure?",
                  ["Yes", "No"],
                  has_shadow=True,
                  on_close=self._quit_on_yes))

  @staticmethod
  def _quit_on_yes(selected):
    # Yes is the first button
    if selected == 0:
      sys.exit(0)
    
def battle_screen(screen, battle):
  battle.battlescreen.screen = screen
  screen.play([Scene([BattleFrame(screen, battle)], -1)], stop_on_resize=True)
    
# Screen.wrapper(BattleFrame)

# Sprites used for the demo
arrow = None
cross_hairs = None

class KeyboardController(DynamicPath):
    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            key = event.key_code
            if key == Screen.KEY_UP:
                self._y -= 1
                self._y = max(self._y, 2)
            elif key == Screen.KEY_DOWN:
                self._y += 1
                self._y = min(self._y, self._screen.height-2)
            elif key == Screen.KEY_LEFT:
                self._x -= 1
                self._x = max(self._x, 3)
            elif key == Screen.KEY_RIGHT:
                self._x += 1
                self._x = min(self._x, self._screen.width-3)
            else:
                return event
        else:
            return event

class TrackingPath(DynamicPath):
    def __init__(self, scene, path):
        super(TrackingPath, self).__init__(scene, 0, 0)
        self._path = path

    def process_event(self, event):
        return event

    def next_pos(self):
        x, y = self._path.next_pos()
        return x + 8, y - 2


class Speak(Sprite):
    def __init__(self, screen, scene, path, text, **kwargs):
        """
        See :py:obj:`.Sprite` for details.
        """
        super(Speak, self).__init__(
            screen,
            renderer_dict={
                "default": SpeechBubble(text, "L")
            },
            path=TrackingPath(scene, path),
            colour=Screen.COLOUR_CYAN,
            **kwargs)


class CrossHairs(Sprite):
    def __init__(self, screen):
        """
        See :py:obj:`.Sprite` for details.
        """
        super(CrossHairs, self).__init__(
            screen,
            renderer_dict={
                "default": StaticRenderer(images=["X"])
            },
            path=MouseController(
                self, screen, screen.width // 2, screen.height // 2),
            colour=Screen.COLOUR_RED)

    def whack(self, sound):
        x, y = self._path.next_pos()
        if self.overlaps(arrow, use_new_pos=True):
            arrow.say("OUCH!")
        else:
            self._scene.add_effect(Print(
                self._screen,
                SpeechBubble(sound), y, x, clear=True, delete_count=50))

def flood_demo(screen):
  scenes = []

  effects = [
    Rain(screen, 200),
    Print(screen,
          FigletText("Flood!", "banner3"),
          (screen.height - 4) // 2,
          colour=Screen.COLOUR_CYAN,
          speed=1,
          stop_frame=30),
  ]
  scenes.append(Scene(effects, -1))

  screen.play(scenes, stop_on_resize=True, repeat=False)

def render_flood_tactic():
  Screen.wrapper(flood_demo)

def fire_demo(screen):
  scenes = []

  effects = [
    Print(screen,
          Fire(screen.height, 80, "*" * 70, 0.8, 60, screen.colours,
               bg=screen.colours >= 256),
          0,
          speed=1,
          transparent=False),
    Print(screen,
          FigletText("Fire!", "banner3"),
          (screen.height - 4) // 2,
          colour=Screen.COLOUR_BLACK,
          speed=1,
          stop_frame=30),
  ]
  scenes.append(Scene(effects, -1))
  screen.play(scenes, stop_on_resize=True, repeat=False)

def render_fire_tactic():
  Screen.wrapper(fire_demo)

def panic_demo(screen):
  scenes = []

  effects = [
    RandomNoise(screen,
                signal=Rainbow(screen,
                               FigletText("Help!"))),
    Print(screen,
          FigletText("Panic!", "banner3"),
          (screen.height - 4) // 2,
          colour=Screen.COLOUR_MAGENTA,
          speed=1,
          stop_frame=30),
  ]
  scenes.append(Scene(effects, -1))  
  screen.play(scenes, stop_on_resize=True, repeat=False)

def render_panic_tactic():
  Screen.wrapper(panic_demo)

sam_default = [
    """
    ______
  .`      `.
 /   -  -   \\
|     __     |
|            |
 \\          /
  '.______.'
""",
    """
    ______
  .`      `.
 /   o  o   \\
|     __     |
|            |
 \\          /
  '.______.'
"""
]
sam_left = """
    ______
  .`      `.
 / o        \\
|            |
|--          |
 \\          /
  '.______.'
"""
sam_right = """
    ______
  .`      `.
 /        o \\
|            |
|          --|
 \\          /
  '.______.'
"""
sam_down = """
    ______
  .`      `.
 /          \\
|            |
|    ^  ^    |
 \\   __     /
  '.______.'
"""
sam_up = """
    ______
  .`  __  `.
 /   v  v   \\
|            |
|            |
 \\          /
  '.______.'
"""

# Images for an arrow Sprite.
left_arrow = """
 /____
/
\\ ____
 \\
"""
up_arrow = """
  /\\
 /  \\
/|  |\\
 |  |
 """
right_arrow = """
____\\
     \\
____ /
    /
"""
down_arrow = """
 |  |
\\|  |/
 \\  /
  \\/
 """
default_arrow = [
    """
  /\\
 /  \\
/|><|\\
 |  |
 """,
    """
  /\\
 /  \\
/|oo|\\
 |  |
 """,
]


# Simple static function to swap between 2 images to make a sprite blink.
def _blink():
    if random.random() > 0.9:
        return 0
    else:
        return 1


class Sam(Sprite):
    """
    Sam Paul sprite - an simple sample animated character.
    """

    def __init__(self, screen, path, start_frame=0, stop_frame=0):
        """
        See :py:obj:`.Sprite` for details.
        """
        super(Sam, self).__init__(
            screen,
            renderer_dict={
                "default": StaticRenderer(images=sam_default, animation=_blink),
                "left": StaticRenderer(images=[sam_left]),
                "right": StaticRenderer(images=[sam_right]),
                "down": StaticRenderer(images=[sam_down]),
                "up": StaticRenderer(images=[sam_up]),
            },
            path=path,
            start_frame=start_frame,
            stop_frame=stop_frame)

    def say(self, text):
        self._scene.add_effect(
            Speak(self._screen, self._scene, self._path, text, delete_count=50))


class Arrow(Sprite):
    """
    Sample arrow sprite - points where it is going.
    """

    def __init__(self, screen, path, colour=Screen.COLOUR_WHITE, start_frame=0,
                 stop_frame=0):
        """
        See :py:obj:`.Sprite` for details.
        """
        super(Arrow, self).__init__(
            screen,
            renderer_dict={
                "default": StaticRenderer(images=default_arrow,
                                          animation=_blink),
                "left": StaticRenderer(images=[left_arrow]),
                "right": StaticRenderer(images=[right_arrow]),
                "down": StaticRenderer(images=[down_arrow]),
                "up": StaticRenderer(images=[up_arrow]),
            },
            path=path,
            colour=colour,
            start_frame=start_frame,
            stop_frame=stop_frame)


class Plot(Sprite):
    """
    Sample Sprite that simply plots an "X" for each step in the path.  Useful
    for plotting a path to the screen.
    """

    def __init__(self, screen, path, colour=Screen.COLOUR_WHITE, start_frame=0,
                 stop_frame=0):
        """
        See :py:obj:`.Sprite` for details.
        """
        super(Plot, self).__init__(
            screen,
            renderer_dict={
                "default": StaticRenderer(images=["X"])
            },
            path=path,
            colour=colour,
            clear=False,
            start_frame=start_frame,
            stop_frame=stop_frame)

def _speak(screen, text, pos, start, tail="L"):
  if tail == 'L':
    x=pos[0]
    y=pos[1]-4
  else:
    x=pos[0]-len(text) - 4 # extra -4 for the boundaries
    y=pos[1]-4
  return Print(
    screen,
    SpeechBubble(text, tail, uni=screen.unicode_aware),
    x=x, y=y,
    colour=Screen.COLOUR_CYAN,
    clear=True,
    start_frame=start,
    stop_frame=start+200)
  
def jeer_demo(screen, narration0, narration1):
  scenes = []
  centre = (screen.width // 2, screen.height // 2)
  podium0 = (16, 4)
  podium1 = (63, 7) # add some to be lower
  
  # Scene 1.
  path0 = Path()
  path1 = Path()
  path0.jump_to(podium0[0]-8, podium0[1])
  path1.jump_to(podium1[0]+8, podium1[1]-3)
  
  effects = [
    Sam(screen, path0),
    Sam(screen, path1),
    # Print(screen, StaticRenderer(["X"]), podium0[1], podium0[0], speed=0),
    # Print(screen, StaticRenderer(["Y"]), podium1[1], podium1[0], speed=0),
    _speak(screen, narration0[1], podium0, 0),
    _speak(screen, narration1[1], podium1, 50, tail='R'),
    Print(screen,
          FigletText("Jeer!", "banner3"),
          (screen.height - 4) // 2,
          colour=Screen.COLOUR_RED,
          speed=1,
          stop_frame=100),
  ]
  
  scenes.append(Scene(effects, -1))
  screen.play(scenes, stop_on_resize=True, repeat=False)

def render_jeer_tactic(narration0, narration1):
  Screen.wrapper(jeer_demo, arguments=[narration0, narration1])

def test_jeer_tactic():
  import insults
  narration0 = ("Jing", "You are a {}!".format(insults.random_diss()))
  narration1 = ("Yan", "No, you are a {}!".format(insults.random_diss()))
  render_jeer_tactic(narration0, narration1)
