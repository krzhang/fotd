import pygame as pg

class Static(pg.sprite.Sprite):
  """ thin wrapper around pg. sprite used for boring sprites """
  
  def __init__(self, x, y, filename):
    pg.sprite.Sprite.__init__(self)
    self.image = pg.image.load(filename).convert_alpha()
    self.rect = self.image.get_rect()
    self.rect.left, self.rect.top = x, y
    self.infobox = False # does not need infobox
    
  def mouseover_info(self):
    """ thing to display in info box when moused over"""
    return None
    
class UnitSpr(Static):
  def __init__(self, x, y, filename, unit):
    super().__init__(x, y, filename)
    self.unit = unit
    unit.sprite = self # is this even a good pattern
    self.infobox = True
    
  def mouseover_info(self):
    return ("UNIT", self.unit)

  def update(self):
    if not self.unit.is_present():
      self.kill()
