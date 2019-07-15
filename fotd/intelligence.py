import random

import numpy as np

import rps
import skills
from mathutils import normalize

class Intelligence(object):
  def __init__(self):
    # TODO: write this later
    pass

class PlayerIntelligence(Intelligence):

  def get_formation(self, battle, armyid):
    return rps.FormationOrder(battle.battlescreen.input_battle_order("FORMATION_ORDER", armyid))

  def get_final(self, battle, armyid):
    return rps.FinalOrder(battle.battlescreen.input_battle_order("FINAL_ORDER", armyid))
  
  # def get_order(self, battle, armyid, order_type):
  #   if order_type == 'FORMATION':
  #     return rps.FormationOrder(battle.battlescreen.input_battle_order(order_type, armyid))
  #   else:
  #     return rps.FinalOrder(battle.battlescreen.input_battle_order(order_type, armyid))

class ArtificialIntelligence(Intelligence):

  def get_formation(self, battle, armyid):
    return rps.FormationOrder(random.choice(['A', 'D', 'I']))
  
  def get_final(self, battle, armyid):
  # 2 paths: RPS and story-driven soul reading
    parmy = battle.armies[1 - armyid].present_units()
    priors = np.array([20,20,20])
    for unit in parmy:
      for sk in unit.character.skills:
        skstr = sk.skill_str
        if skstr in skills.SKILLS:
          priors += np.array(skills.SKILLS[skstr]["ai_eval"])
  # adjusting for size
        # import pdb; pdb.set_trace()
    priors += np.array([1, 0, 0])*(battle.armies[1-armyid].str_estimate() -
                battle.armies[armyid].str_estimate())
  # TODO: adjusting for battlefield conditions
    m = min(priors)
    if m < 0:
      priors += np.array([1-m, 1-m, 1-m])
      assert min(priors) > 0
    newpriors = normalize(priors)
    battle.battlescreen.yprint("  AI predicts player (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*newpriors))
    counters = np.array(list(newpriors[2:]) + list(newpriors[:2]))
    battle.battlescreen.yprint("  AI counterpicks    (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*counters))
    return rps.FinalOrder(np.random.choice(['A', 'D', 'I'], p=counters))

  # def get_order(self, battle, armyid, order_type):
  #   if order_type == 'FORMATION':
  #     return rps.FormationOrder(self.get_formation(battle, armyid))
  #   else:
  #     return rps.FinalOrder(self.get_final(battle, armyid))
  
class RockIntelligence(Intelligence):

  def get_formation(self, battle, armyid):
    return rps.FormationOrder('A')

  def get_final(self, battle, armyid):
    return rps.FinalOrder('A')

class PaperIntelligence(Intelligence):

  def get_formation(self, battle, armyid):
    return rps.FormationOrder('D')

  def get_final(self, battle, armyid):
    return rps.FinalOrder('D')

class ScissorsIntelligence(Intelligence):

  def get_formation(self, battle, armyid):
    return rps.FormationOrder('I')

  def get_final(self, battle, armyid):
    return rps.FinalOrder('I')

INTELLIGENCE_FROM_TYPE = {'INT_AI_NORMAL': ArtificialIntelligence,
                          'INT_PLAYER': PlayerIntelligence,
                          'INT_AI_ROCK': RockIntelligence,
                          'INT_AI_PAPER': PaperIntelligence,
                          'INT_AI_SCISSORS': ScissorsIntelligence,
                          }
