from asciimatics.effects import Cycle, Print, Stars
from asciimatics.renderers import SpeechBubble, FigletText, Box
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.sprites import Arrow, Plot, Sam
from asciimatics.paths import Path
from asciimatics.exceptions import ResizeScreenError
from asciimatics.event import KeyboardEvent
from asciimatics.widgets import Frame, Layout, MultiColumnListBox, Widget, Label, TextBox
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, StopApplication
from collections import defaultdict
from asciimatics.effects import Sprite, Print
from asciimatics.event import KeyboardEvent, MouseEvent
from asciimatics.exceptions import ResizeScreenError
from asciimatics.renderers import StaticRenderer, SpeechBubble, FigletText
from asciimatics.screen import Screen
from asciimatics.paths import DynamicPath
from asciimatics.sprites import Arrow
from asciimatics.scene import Scene

import sys

def _speak(screen, text, pos, start):
  return Print(
    screen,
    SpeechBubble(text, "L", uni=screen.unicode_aware),
    x=pos[0] + 4, y=pos[1] - 4,
    colour=Screen.COLOUR_CYAN,
    clear=True,
    start_frame=start,
    stop_frame=start+50)


class BattleFrame(Frame):
  def __init__(self, screen, battle):
    super().__init__(screen,
                     screen.height,
                     screen.width,
                     has_border=False)
    self.battle = battle
    layout = Layout([1], fill_frame=True)
    self.statline = TextBox(1, as_string=True)
    self.statline.disabled = True
    self.armystats = TextBox(20, as_string=True)
    self.armystats.disabled = True
    self.console = TextBox(3, as_string=True)
    self.console.disabled = True
    self.add_layout(layout)
    layout.add_widget(self.statline)
    layout.add_widget(self.armystats)
    layout.add_widget(self.console)
    self.fix()

  def process_event(self, event):
    # Do the key handling for this Frame.
    if isinstance(event, KeyboardEvent):
      if event.key_code in [ord('q'), ord('Q'), Screen.ctrl("c")]:
        raise StopApplication("User quit")
      elif event.key_code in [ord("r"), ord("R")]:
        pass
        # Force a refresh for improved responsiveness
      self._last_frame = 0

    # Now pass on to lower levels for normal handling of the event.
    return super().process_event(event)

def battle_screen(screen, battle):
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


class MouseController(DynamicPath):
    def __init__(self, sprite, scene, x, y):
        super(MouseController, self).__init__(scene, x, y)
        self._sprite = sprite

    def process_event(self, event):
        if isinstance(event, MouseEvent):
            self._x = event.x
            self._y = event.y
            if event.buttons & MouseEvent.DOUBLE_CLICK != 0:
                # Try to whack the other sprites when mouse is clicked
                self._sprite.whack("KERPOW!")
            elif event.buttons & MouseEvent.LEFT_CLICK != 0:
                # Try to whack the other sprites when mouse is clicked
                self._sprite.whack("BANG!")
            elif event.buttons & MouseEvent.RIGHT_CLICK != 0:
                # Try to whack the other sprites when mouse is clicked
                self._sprite.whack("CRASH!")
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
  
def demo_top(screen):
  screen.play([Scene([DemoFrame(screen)], -1)], stop_on_resize=True)

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

def main_screen(screen):
    global arrow, cross_hairs
    arrow = InteractiveArrow(screen)
    cross_hairs = CrossHairs(screen)

    # scenes = []
    # effects = [
    #     Print(screen, FigletText("Hit the arrow with the mouse!", "digital"),
    #           y=screen.height//3-3),
    #     Print(screen, FigletText("Press space when you're ready.", "digital"),
    #           y=2 * screen.height//3-3),
    # ]
    # scenes.append(Scene(effects, -1))

    effects = [
        arrow,
        cross_hairs
    ]
    scenes.append(Scene(effects, -1))

    screen.play(scenes, stop_on_resize=True)

def blank_screen(screen):
  pass
