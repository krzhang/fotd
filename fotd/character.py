import skills

STAT_BASES = {"power":"power_base",
              "intel":"intel_base",
              "pol":"pol_base",
              "cha":"cha_base"}

class Character(object):
  def __init__(self, name, title, power, intel, pol, cha, coolness, bravery, skillstrs, gender='M'):
    self.id = name + title # this really needs to be rewritten
    self.name = name
    self.gender = gender
    self.title = title
    self.power_base = power
    self.intel_base = intel
    self.pol_base = pol
    self.cha_base = cha
    self.coolness_base = coolness
    self.bravery_base = bravery
    self.skillstrs = skillstrs
    self.skills = [skills.Skill(s) for s in skillstrs]
    self.health = 100
    self.items = []
    self.status = []
    self.calc_attributes()
    self.color = ""

  def __eq__(self, other):
    return hasattr(self, "id") and hasattr(other, "id") and self.id == other.id
    
  def calc_attributes(self):
    for s in STAT_BASES:
      setattr(self, s, getattr(self, STAT_BASES[s]))
    # do items stuff

  def copy(self):
    return Character(self.name, self.title, self.power_base, self.intel_base, self.pol_base, self.cha_base, self.coolness_base, self.bravery_base, self.skillstrs.copy(), self.gender)
    
  def equip(self, item):
    self.items.append(item)
    self.calc_attributes()

  def __str__(self):
    return self.name

  def color_name(self):
    return "$[{}]${}$[7]$".format(self.color, self.name)
  
  def title_fancy(self):
    if self.title:
      return " $[4]$-=$[7]${}$[4]$=-$[7]$".format(self.title) # eventually move out
    return ""

  def full_name_fancy(self):
    return self.color_name() + self.title_fancy()

  
TITLES = [
  "Finalmente",
  "Indubtibly",
  "Nine Dragons", # see more Water Margin
]
