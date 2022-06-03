import os
import pygame
import sys
import yaml

from pathlib import Path

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
