import status

class Relations(object):
  """ a class to store relationships in a single context (such as a battle) """

  def __init__(self, units):
    pass

  def aid_chance(self, source, target, context):
    # maybe source will save target
    pass

  def is_family(self, source, target):
    # if target considers source family
    pass

  # MVP ideas:

  def is_ruler(self, source, target):
    pass

  def is_subordinate(self, source, target):
    pass

  def has_vendetta(self, source, target):
    pass

  def is_flanking(self, source, target):
    pass
