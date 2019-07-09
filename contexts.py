# from collections import UserDict
# 
# only if we eventually inherit here.
# [The problem with inheriting from dict and list in Python - Trey Hunner](https://treyhunner.com/2019/04/why-you-shouldnt-inherit-from-list-and-dict-in-python/)

class Context(object):
  def __init__(self, battle, opt={}):
    self.battle = battle
    self.opt = opt
    for o in opt:
      setattr(self, o, opt[o])

  def copy(self, additional_opt):
    """Make a copy with the same battle context"""
    nopt = self.opt.copy()
    nopt.update(additional_opt)
    return Context(self.battle, opt=nopt)

  def rebase(self, opt):
    """Make a copy with the same battle context"""
    return Context(self.battle, opt=opt)

  def rebase_switch(self):
    """Most common usecase: create a context with switched source/ctargets. """
    return self.rebase({"ctarget":self.csource, "csource":self.ctarget})

  # def speech(self, narrator, text):
  #   """
  #   Ex: context.speech('csource', 'yo{ctarget}...')
  #   should put in the context and then pass to the speaker
  #   """
  #   self.opt[narrator].speech(text.format(**self.opt))
  
