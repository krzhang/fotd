import os
import pygame
import sys
import yaml

from pathlib import Path

def read_single_keypress():
  """Waits for a single keypress on stdin.

  [How do I make python to wait for a pressed key - Stack Overflow](https://stackoverflow.com/questions/983354/how-do-i-make-python-to-wait-for-a-pressed-key#comment90923542_6599441)

  This is a silly function to call if you need to do it a lot because it has
  to store stdin's current setup, setup stdin for reading single keystrokes
  then read the single keystroke then revert stdin back after reading the
  keystroke.
  
  Returns a tuple of characters of the key that was pressed - on Linux, 
  pressing keys like up arrow results in a sequence of characters. Returns 
  ('\x03',) on KeyboardInterrupt which can happen when a signal gets
  handled.
  
  """
  import termios, fcntl, sys
  fd = sys.stdin.fileno()
  # save old state
  flags_save = fcntl.fcntl(fd, fcntl.F_GETFL)
  attrs_save = termios.tcgetattr(fd)
  # make raw - the way to do this comes from the termios(3) man page.
  attrs = list(attrs_save) # copy the stored version to update
  # iflag
  attrs[0] &= ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK
                | termios.ISTRIP | termios.INLCR | termios. IGNCR
                | termios.ICRNL | termios.IXON )
  # oflag
  attrs[1] &= ~termios.OPOST
  # cflag
  attrs[2] &= ~(termios.CSIZE | termios. PARENB)
  attrs[2] |= termios.CS8
  # lflag
  attrs[3] &= ~(termios.ECHONL | termios.ECHO | termios.ICANON
                | termios.ISIG | termios.IEXTEN)
  termios.tcsetattr(fd, termios.TCSANOW, attrs)
  # turn off non-blocking
  fcntl.fcntl(fd, fcntl.F_SETFL, flags_save & ~os.O_NONBLOCK)
  # read a single keystroke
  ret = []
  try:
    ret.append(sys.stdin.read(1)) # returns a single character
    fcntl.fcntl(fd, fcntl.F_SETFL, flags_save | os.O_NONBLOCK)
    c = sys.stdin.read(1) # returns a single character
    while len(c) > 0:
      ret.append(c)
      c = sys.stdin.read(1)
  except KeyboardInterrupt:
    ret.append('\x03')
  finally:
    # restore old state
    termios.tcsetattr(fd, termios.TCSAFLUSH, attrs_save)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags_save)
  if ret[0] == 'q':
    sys.exit(0)
  return tuple(ret)

def clear_screen():
  os.system('cls' if os.name == 'nt' else 'clear')

def str_to_bool(string):
  if string == "True":
    return True
  assert string == "False"
  return False

def timeit(f):

  def timed(*args, **kw):
    ts = pygame.time.get_ticks()
    result = f(*args, **kw)
    te = pygame.time.get_ticks()
    print('func:%r args:[%r, %r] took: %d millis' % \
          (f.__name__, args, kw, te-ts))
    return result

  return timed

def parse_yaml(path, module):
  objects = {}
  with open(path, 'r') as f:
    data = yaml.safe_load(f)
    for u in data:
      u_class = module.__dict__[list(u.keys())[0]]
      kwargs = list(u.values())[0]
      objects[kwargs['name']] = u_class(**kwargs)
  return objects

def distance(p0, p1):
  return abs(p0[0] - p1[0]) + abs(p0[1] - p1[1])

def resize_keep_ratio(size, max_size):
  w, h = size
  max_w, max_h = max_size
  resize_ratio = min(max_w / w, max_h / h)
  return int(w * resize_ratio), int(h * resize_ratio)

def resize_cover(size, max_size):
  w, h = size
  max_w, max_h = max_size
  resize_ratio = max(max_w / w, max_h / h)
  return int(w * resize_ratio), int(h * resize_ratio)

def center(rect1, rect2, xoffset=0, yoffset=0):
  """Center rect2 in rect1 with offset."""
  return (rect1.centerx - rect2.centerx + xoffset, rect1.centery - rect2.centery + yoffset)

def return_to_os(*args):
  pygame.quit()
  sys.exit(0)

def get_version():
  version_file_path = Path(__file__).absolute().parent / 'VERSION'
  return open(version_file_path).read().strip('\n')
