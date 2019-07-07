import textutils
from textutils import yprint

class Position(object):
  def __init__(self, battle, initial_unit, hqid=None):
    self.battle = battle
    self.initial_unit = initial_unit
    self.units = [[],[]]
    self.hqid = hqid # None is neither: otherwise the hq of the corresponding army

  def __str__(self):
    if self.hqid is not None:
      return "the army {} HQ".format(self.hqid)
    else:
      return "the field around {}".format(self.initial_unit)

  def add_unit(self, unit):
    self.units[unit.armyid].append(unit)
    # unit.position = self

  def display(self,debug=False):
    yprint("In {}:".format(str(self)),debug)
    for i in [0,1]:
      for u in self.units[i]:
        if u.is_present():
          charstr = "{} {}".format(repr(u), " ".join((repr(s) for s in u.character.skills)))
          yprint(charstr,debug)
          healthbar = textutils.disp_bar(20, u.size_base, u.size)
          yprint("  {} {} (SP: {}) {}".format(healthbar, u.size_repr(), u.speed, u.status_real_repr()),debug)

  def remove_unit(self, unit):
    self.units[unit.armyid].remove(unit)

  def units_by_army(self, armyid):
    return self.units[armyid]

  def is_empty(self):
    return self.units == [[],[]]
