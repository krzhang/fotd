import pygame as pg
import settings_battle
import resources

class Static(pg.sprite.Sprite):
  """ thin wrapper around pg. sprite used for boring sprites """
  
  def __init__(self, view, x, y, filename):
    pg.sprite.Sprite.__init__(self)
    self.view = view
    self.image = pg.image.load(filename).convert_alpha()
    self.rect = self.image.get_rect()
    self.rect.left, self.rect.top = x, y
    self.infobox = False # does not need infobox
    view.all_sprites.add(self)
    
  def mouseover_info(self):
    """ thing to display in info box when moused over"""
    return None
    
class UnitSpr(Static):
  def __init__(self, view, x, y, filename, unit, facing):
    """
    [facing]: 
    "NORTH" or "SOUTH"
    """
    super().__init__(view, x, y, filename)
    self.unit = unit
    self.facing = facing
    unit.sprite = self # is this even a good pattern
    self.infobox = True

    self.size_bar_back = UnitSizeBar(view, resources.SPRITES_PATH / "health-red.png", self, "MAX")
    self.size_bar_mid = UnitSizeBar(view, resources.SPRITES_PATH / "health-yellow.png", self, "LAST_TURN")
    self.size_bar_front = UnitSizeBar(view, resources.SPRITES_PATH / "health-green.png", self, "CURRENT")

    x = self.rect.left - 10
    if self.facing == "SOUTH":
      y = self.rect.top - 70
      y_inc = -45 # how much space to allocate for each skill sprite
    else:
      y = self.rect.bottom + 30
      y_inc = 45
    self.skill_sprs = []
    for i, s in enumerate(unit.skills):
      self.skill_sprs.append(SkillSpr(view, x, y, resources.SKILLS_PATH / (str(s) + ".png"),
                                      self, s))
      y += y_inc

  def mouseover_info(self):
    return ("UNIT", self.unit)

  def update(self):
    if not self.unit.is_present():
      self.kill()

class UnitSizeBar(pg.sprite.Sprite):
  """ 
  thanks to https://www.youtube.com/watch?v=oYomaFLiAFU&t=490s for tutorial

  x, y will be center of unit sprite
  """
  def __init__(self, view, filename, unit_spr, layer):
    pg.sprite.Sprite.__init__(self)
    self.view = view
    self.filename = filename
    self.unit_spr = unit_spr
    self.size_max = settings_battle.ARMY_SIZE_MAX
    self.image = pg.image.load(filename)
    self.layer = layer
    # self.image = pg.transform.scale(self.image, (x,y)) # good to keep in mind
    # self.rect = self.image.get_rect()
    # self.rect.left = x - 64
    # self.rect.centery = y
    self.update()
    # we need update first to define a rect()
    view.all_sprites.add(self)
    self.infobox = False

  def update(self):
    if not self.unit_spr:
      self.kill()
    if self.layer == "CURRENT":
      self.image = pg.transform.scale(self.image, (int(self.unit_spr.unit.size)/self.size_max*128, 10))
    elif self.layer == "LAST_TURN":
      self.image = pg.transform.scale(self.image, (int(self.unit_spr.unit.last_turn_size)/self.size_max*128, 10))
    else:
      assert self.layer == "MAX"
      self.image = pg.transform.scale(self.image, (128, 10))
      
    self.rect = self.image.get_rect()
    self.rect.left = self.unit_spr.rect.centerx - 64
    if self.unit_spr.facing == "SOUTH":
      self.rect.centery = self.unit_spr.rect.top - 10
    else:
      assert self.unit_spr.facing == "NORTH"
      self.rect.centery = self.unit_spr.rect.bottom + 10

class SkillSpr(Static):
  """ a skill sprite """
  def __init__(self, view, x, y, filename, unit_spr, skill):
    super().__init__(view, x, y, filename)
    self.image = pg.transform.scale(self.image, (40, 40))
    self.unit_spr = unit_spr
    self.skill = skill
    view.all_sprites.add(self)
    self.infobox = False # change to True later

  def update(self):
    pass # these never change!
  
