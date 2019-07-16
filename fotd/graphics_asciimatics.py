from collections import defaultdict
import sys

from pyfiglet import Figlet
from asciimatics.effects import Cycle, Print, Stars, Sprite, RandomNoise
from asciimatics.event import KeyboardEvent, MouseEvent
from asciimatics.exceptions import ResizeScreenError, StopApplication
from asciimatics.particles import Explosion, StarFirework, DropScreen, Rain
from asciimatics.paths import Path, DynamicPath
from asciimatics.renderers import StaticRenderer, SpeechBubble, FigletText, Rainbow
from asciimatics.sprites import Arrow, Plot, Sam
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
    
    # # Render visible portion of the text.
    # for line, (text, _, _) in enumerate(display_text):
    #   if self._start_line <= line < self._start_line + height:
    #     self._frame.canvas.print_at(
    #       text,
    #       # _enforce_width(text[display_start_column:], self.width,
    #       #                self._frame.canvas.unicode_aware),
    #       self._x + self._offset,
    #       self._y + line - self._start_line,
    #       colour, attr, bg)
        
    # for y, l in enumerate(self.value):
    #   self._scene.add_effect(Print(self._screen,
    #                         StaticRenderer(images=[self._render(l)]), x=0, y=y, colour=7))
    image, colours = StaticRenderer(self.value).rendered_text
    for (i, line) in enumerate(image):
      self._frame.canvas.paint(line, self._x, self._y + i, self._colour,
                                   attr=self._attr,
                                   bg=self._bg,
                                   transparent=self._transparent,
                                   colour_map=colours[i])

    # Since we switch off the standard cursor, we need to emulate our own
    # if we have the input focus.
    # if self._has_focus:
    #   line = display_text[display_line][0]
    #   text_width = self.string_len(line[display_start_column:display_column])
    #   self._draw_cursor(
    #     " " if display_column >= len(line) else line[display_column],
    #     frame_no,
    #     self._x + self._offset + text_width,
    #     self._y + display_line - self._start_line)


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
    # self.statline.value = [self._render(l) for l in self.battle.battlescreen._disp_statline()]
    # self.armystats.value = [self._render(l) for l in self.battle.battlescreen._disp_armies()]
    # self.console.value = [self._render(l) for l in self.battle.battlescreen._disp_console()]
     # effects = []
        
  def process_event(self, event):
    # Do the key handling for this Frame.
    if isinstance(event, KeyboardEvent):
      if event.key_code in [ord('q'), ord('Q'), Screen.ctrl("c")]:
        self._quit()
      elif event.key_code in [ord("r"), ord("R")]:
        # st = self.battle.battlescreen._disp_statline() # 2 lines
        # ar = self.battle.battlescreen._disp_armies() # 18 lines
        # co = self.battle.battlescreen._disp_console() # 3 lines
        # fo = self.battle.battlescreen._disp_footerline("") # 1 line
        # assert len(st + ar + co) == self.battle.battlescreen.max_screen_len - 1
        # for y, l in enumerate(st + ar + co):
        #   self._scene.add_effect(Print(self._screen,
        #                         StaticRenderer(images=[self._render(l)]), x=0, y=y, colour=7))
        # Force a refresh for improved responsiveness

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


class InteractiveArrow(Arrow):
    def __init__(self, screen):
        """
        See :py:obj:`.Sprite` for details.
        """
        super(InteractiveArrow, self).__init__(
            screen,
            path=KeyboardController(
                screen, screen.width // 2, screen.height // 2),
            colour=Screen.COLOUR_GREEN)

    def say(self, text):
        self._scene.add_effect(
            Speak(self._screen, self._scene, self._path, text, delete_count=50))


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

def demo(screen):
  scenes = []
  centre = (screen.width // 2, screen.height // 2)
  podium = (8, 5)
  
  # Scene 1.
  path = Path()
  path.jump_to(-20, centre[1])
  path.move_straight_to(centre[0], centre[1], 10)
  path.wait(30)
  path.move_straight_to(podium[0], podium[1], 10)
  path.wait(100)
  
  effects = [
      Arrow(screen, path, colour=Screen.COLOUR_BLUE),
      _speak(screen, "WELCOME TO ASCIIMATICS", centre, 30),
      _speak(screen, "My name is Aristotle Arrow.", podium, 110),
      _speak(screen,
             "I'm here to help you learn ASCIImatics.", podium, 180),
  ]
  scenes.append(Scene(effects))
  
  # Scene 2.
  path = Path()
  path.jump_to(podium[0], podium[1])
  
  effects = [
      Arrow(screen, path, colour=Screen.COLOUR_GREEN),
      _speak(screen, "Let's start with the Screen...", podium, 10),
      _speak(screen, "This is your Screen object.", podium, 80),
      Print(screen,
            Box(screen.width, screen.height, uni=screen.unicode_aware),
            0, 0, start_frame=90),
      _speak(screen, "It lets you play a Scene like this one I'm in.",
             podium, 150),
      _speak(screen, "A Scene contains one or more Effects.", podium, 220),
      _speak(screen, "Like me - I'm a Sprite!", podium, 290),
      _speak(screen, "Or these Stars.", podium, 360),
      _speak(screen, "As you can see, the Screen handles them both at once.",
             podium, 430),
      _speak(screen, "It can handle as many Effects as you like.",
             podium, 500),
      _speak(screen, "Please press <SPACE> now.", podium, 570),
      Stars(screen, (screen.width + screen.height) // 2, start_frame=360)
  ]
  scenes.append(Scene(effects, -1))
  
  # # Scene 3.
  # path = Path()
  # path.jump_to(podium[0], podium[1])
  
  # effects = [
  #     Arrow(screen, path, colour=Screen.COLOUR_GREEN),
  #     _speak(screen, "This is a new Scene.", podium, 10),
  #     _speak(screen, "The Screen stops all Effects and clears itself between "
  #                    "Scenes.",
  #            podium, 70),
  #     _speak(screen, "That's why you can't see the Stars now.", podium, 130),
  #     _speak(screen, "(Though you can override that if you need to.)", podium,
  #            200),
  #     _speak(screen, "Please press <SPACE> now.", podium, 270),
  # ]
  # scenes.append(Scene(effects, -1))
  
  # # Scene 4.
  # path = Path()
  # path.jump_to(podium[0], podium[1])
  
  # effects = [
  #     Arrow(screen, path, colour=Screen.COLOUR_GREEN),
  #     _speak(screen, "So, how do you design your animation?", podium, 10),
  #     _speak(screen, "1) Decide on your cinematic flow of Scenes.", podium,
  #            80),
  #     _speak(screen, "2) Create the Effects in each Scene.", podium, 150),
  #     _speak(screen, "3) Pass the Scenes to the Screen to play.", podium,
  #            220),
  #     _speak(screen, "It really is that easy!", podium, 290),
  #     _speak(screen, "Just look at this sample code.", podium, 360),
  #     _speak(screen, "Please press <SPACE> now.", podium, 430),
  # ]
  # scenes.append(Scene(effects, -1))
  
  # # Scene 5.
  # path = Path()
  # path.jump_to(podium[0], podium[1])
  
  # effects = [
  #     Arrow(screen, path, colour=Screen.COLOUR_GREEN),
  #     _speak(screen, "There are various effects you can use.  For "
  #                    "example...",
  #            podium, 10),
  #     Cycle(screen,
  #           FigletText("Colour cycling"),
  #           centre[1] - 5,
  #           start_frame=100),
  #     Cycle(screen,
  #           FigletText("using Figlet"),
  #           centre[1] + 1,
  #           start_frame=100),
  #     _speak(screen, "Look in the effects module for more...",
  #            podium, 290),
  #     _speak(screen, "Please press <SPACE> now.", podium, 360),
  # ]
  # scenes.append(Scene(effects, -1))
  
  # # Scene 6.
  # path = Path()
  # path.jump_to(podium[0], podium[1])
  # curve_path = []
  # for i in range(0, 11):
  #     curve_path.append(
  #         (centre[0] + (screen.width / 4 * math.sin(i * math.pi / 5)),
  #          centre[1] - (screen.height / 4 * math.cos(i * math.pi / 5))))
  # path2 = Path()
  # path2.jump_to(centre[0], centre[1] - screen.height // 4)
  # path2.move_round_to(curve_path, 60)
  
  # effects = [
  #     Arrow(screen, path, colour=Screen.COLOUR_GREEN),
  #     _speak(screen, "Sprites (like me) are also an Effect.", podium, 10),
  #     _speak(screen, "We take a pre-defined Path to follow.", podium, 80),
  #     _speak(screen, "Like this one...", podium, 150),
  #     Plot(screen, path2, colour=Screen.COLOUR_BLUE, start_frame=160,
  #          stop_frame=300),
  #     _speak(screen, "My friend Sam will now follow it...", podium, 320),
  #     Sam(screen, copy.copy(path2), start_frame=380),
  #     _speak(screen, "Please press <SPACE> now.", podium, 420),
  # ]
  # scenes.append(Scene(effects, -1))
  
  # # Scene 7.
  # path = Path()
  # path.jump_to(podium[0], podium[1])
  # path.wait(60)
  # path.move_straight_to(-5, podium[1], 20)
  # path.wait(300)
  
  # effects = [
  #     Arrow(screen, path, colour=Screen.COLOUR_GREEN),
  #     _speak(screen, "Goodbye!", podium, 10),
  #     Cycle(screen,
  #           FigletText("THE END!"),
  #           centre[1] - 4,
  #           start_frame=100),
  #     Print(screen, SpeechBubble("Press X to exit"), centre[1] + 6,
  #           start_frame=150)
  # ]
  # scenes.append(Scene(effects, 500))
  
  screen.play(scenes, stop_on_resize=True)


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
  
def _speak(screen, text, pos, start, tail="L"):
  if tail == 'L':
    x=pos[0] + 4
    y=pos[1] - 4
  else:
    x=pos[0] - 4
    y=pos[1] - 4
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
  podium0 = (8, 5)
  podium1 = (78, 5)
  spodium0 = (16, 5)
  spodium1 = (50, 8)
  
  # Scene 1.
  path0 = Path()
  path1 = Path()
  path0.jump_to(podium0[0], podium0[1])
  path1.jump_to(podium1[0], podium1[1])
  
  effects = [
    Sam(screen, path0),
    Sam(screen, path1),
    _speak(screen, narration0[1], spodium0, 0),
    _speak(screen, narration1[1], spodium1, 0, tail='R'),
    Print(screen,
          FigletText("Jeer!", "banner3"),
          (screen.height - 4) // 2,
          colour=Screen.COLOUR_RED,
          speed=1,
          stop_frame=30),
  ]
  
  scenes.append(Scene(effects, -1))
  screen.play(scenes, stop_on_resize=True, repeat=False)

def render_jeer_tactic(narration0, narration1):
  Screen.wrapper(jeer_demo, arguments=[narration0, narration1])
