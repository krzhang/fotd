""" 
Resource loader

format stolen from Ice Emblem
"""

from typing import List, Tuple

import pygame
import logging

from pathlib import Path
from xml.etree import ElementTree

RESOURCES_PATH = Path(__file__).absolute().parent / 'resources'  #: resources directory
IMAGE_PATH =   RESOURCES_PATH / 'images'  #: images directory
FONTS_PATH =   RESOURCES_PATH / 'fonts'
SPRITES_PATH = RESOURCES_PATH / 'sprites'
SKILLS_PATH = IMAGE_PATH / "skills"

__logger = logging.getLogger(__name__)

def skill_filename(skill):
  return SKILLS_PATH / (skill.skill_str + ".png")

def skillcard_filename(skillcard):
  return SKILLS_PATH / (skillcard.sc_str + ".png") 
# def __load_log(path):
#   __logger.debug('Loading %s', path)

# def load_image(fname):
#   path = str(IMAGE_PATH / fname)
#   __load_log(path)
#   return pygame.image.load(path)

IMAGE_CACHE= {}

def get_image(filename):
  if not filename in IMAGE_CACHE:
    IMAGE_CACHE[filename] = pygame.image.load(filename)
  return IMAGE_CACHE[filename]

def get_image_misc(filename_short):
  return get_image(IMAGE_PATH / (filename_short + ".png"))

def get_image_skill(skill):
  return get_image(skill_filename(skill))

# def sprite_path(name: str):
#   """
#   Return the path to a sprite by filename with or without file extension.

#   :param name: The name of the sprite. Doesn't need file extension. png and jpg files are supported.
#   :return: the absolute path to a sprite resource.
#   """
#   if '.' not in name:
#     for f in SPRITES_PATH.iterdir():
#       if f.name == name + '.png' or f.name == name + '.jpg':
#         name = f.name
#         break
#   return SPRITES_PATH / name


