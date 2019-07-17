
# from collections import UserDict
# 
# only if we eventually inherit here.
# [The problem with inheriting from dict and list in Python - Trey Hunner](https://treyhunner.com/2019/04/why-you-shouldnt-inherit-from-list-and-dict-in-python/)

class Context(object):

  # currently a terrible more complex version of a dictionary. Sigh
  
  def __init__(self, opt):
    self.opt = opt
    for o in opt:
      setattr(self, o, opt[o])

  def __getitem__(self, key):
    return self.opt[key]

  def __contains__(self, key):
    return key in self.opt

  def __iter__(self):
    return iter(self.opt)
  
  def copy(self, additional_opt):
    """Make a copy with the same battle context"""
    nopt = self.opt.copy()
    nopt.update(additional_opt)
    return Context(nopt)

  def clean_switch(self, additional_opt={}):
    """Most common usecase: create a context with switched source/ctargets. """
    return Context({"ctarget":self.csource, "csource":self.ctarget}).copy(additional_opt)

  # def speech(self, narrator, text):
  #   """
  #   Ex: context.speech('csource', 'yo{ctarget}...')
  #   should put in the context and then pass to the speaker
  #   """
  #   self.opt[narrator].speech(text.format(**self.opt))
  
