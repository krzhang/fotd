import pygame as pg
import settings_battle
import resources
import skills
import colors

class Static(pg.sprite.Sprite):
  """ thin wrapper around pg. sprite used for boring sprites """
  
  def __init__(self, view, x, y, filename):
    pg.sprite.Sprite.__init__(self)
    self.view = view
    self.image = resources.get_image(filename).convert_alpha()
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
    # if self.facing == "SOUTH":
    #   y = self.rect.top - 70
    #   y_inc = -45 # how much space to allocate for each skill sprite
    # else:
    #   y = self.rect.bottom + 30
    #   y_inc = 45
    # self.skill_sprs = []
    # for i, s in enumerate(unit.skills):
    #   self.skill_sprs.append(SkillSpr(view, x, y, resources.SKILLS_PATH / (str(s) + ".png"),
    #                                   self, s))
    #   y += y_inc

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
    self.image = resources.get_image(filename)
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

# class SkillSpr(Static):
#   """ a skill sprite """
#   def __init__(self, view, x, y, filename, unit_spr, skill):
#     super().__init__(view, x, y, filename)
#     self.image = pg.transform.scale(self.image, (40, 40))
#     self.unit_spr = unit_spr
#     self.skill = skill
#     view.all_sprites.add(self)
#     self.infobox = True
    
#     # create potential skillcards
#     self.skillcard_sprs = {}
#     if skill.skillcard:
#       sc_abs = skills.SKILLCARDS[skill.skillcard]
#       x_ctr = self.rect.left + 45
#       for order in ['A', 'D', 'I']:
#         if sc_abs.bulb[order]:
#           filename = resources.skillcard_filename(sc_abs) 
#           sc_spr = SkillCardSpr(view, x_ctr, y,
#                                 filename,
#                                 self,
#                                 skill.skill_str,
#                                 skill.skillcard,
#                                 order)
#           self.skillcard_sprs[order] = sc_spr
#           x_ctr += 45

#   def mouseover_info(self):
#     return ("SKILL", self.skill)
          
#   def update(self):
#     pass # these never change!

class TableauCardSpr(pg.sprite.Sprite):
  """ 
  skillcards sprites. These have colors since they correspond to phases
  """

  def __init__(self, view, imagebox, x, y, filename, tableaucard):
    
    pg.sprite.Sprite.__init__(self)
    self.view = view
    self.imagebox = imagebox
    self.filename = filename
    self.image = pg.transform.scale(resources.get_image(filename), ((40, 40))) # copy
    self.image.set_colorkey(self.image.get_at((0, 0)))
    # hack; this sets the upper left pixel's color (probably white) to the transparency color
    self.tableaucard = tableaucard
    self.skillcard = tableaucard.skillcard
    self.army = self.tableaucard.unit.army
    self.order = self.skillcard.order
    self.rect = self.image.get_rect()
    self.rect.left, self.rect.top = x, y
    self.x = x
    self.y = y
    color_image = pg.Surface(self.image.get_size()).convert_alpha()
    if self.order == "A":
      background = colors.PColors.RED
    elif self.order == "D":
      background = colors.PColors.BLUE
    elif self.order == 'I':
      background = colors.PColors.YELLOW
    color_image.fill(background)
    self.image.blit(color_image, (0,0), special_flags=pg.BLEND_RGBA_MULT)
    view.all_sprites.add(self)
    self.infobox = True

  def mouseover_info(self):
    return ("SKILLCARD", self.skillcard)
    
  def update(self):
    visibility = self.tableaucard.visibility[self.view.army.armyid]
    if not visibility:
      self.rect.left, self.rect.top = 2000, 2000
    else:
      # make copy of self and put it on that surface. A bit janky
      # self.imagebox.image_to_surface(self.image, 40, 40)
      self.imagebox.sprite_to_surface(self)
      
