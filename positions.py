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
    self.units[unit.army.armyid].append(unit)
    # unit.position = self

  def remove_unit(self, unit):
    self.units[unit.army.armyid].remove(unit)

  def units_by_army(self, armyid):
    return self.units[armyid]

  def is_empty(self):
    return self.units == [[],[]]
