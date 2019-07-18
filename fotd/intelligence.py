import random

import numpy as np

import rps
import skills
from mathutils import normalize

class Intelligence(object):
  def __init__(self, army):
    # TODO: write this later
    self.army = army
    self.armyid = self.army.armyid

class PlayerIntelligence(Intelligence):

  def get_formation(self, battle):
    return rps.FormationOrder(battle.battlescreen.input_battle_order("FORMATION_ORDER", self.armyid))

  def get_final(self, battle):
    return rps.FinalOrder(battle.battlescreen.input_battle_order("FINAL_ORDER", self.armyid))
  
  # def get_order(self, battle, armyid, order_type):
  #   if order_type == 'FORMATION':
  #     return rps.FormationOrder(battle.battlescreen.input_battle_order(order_type, armyid))
  #   else:
  #     return rps.FinalOrder(battle.battlescreen.input_battle_order(order_type, armyid))

class ArtificialIntelligence(Intelligence):

  
  def army_power_estimate(self, army):
    return sum([u.size for u in army.present_units()], 0)
  
  def evaluate_state(self, battle, army):
    """
    evaluate the state of armyid, which could be self or someone else, by the strengths of
    the 3 stacks and the army strengths.

    should use army.state_viewed_by
    """
    parmy = army.present_units()
    priors = np.array([20, 20, 20])
    for unit in parmy:
      for sk in unit.character.skills:
        skstr = sk.skill_str
        if skstr in skills.SKILLS:
          priors += np.array(skills.SKILLS[skstr]["ai_eval"])

    #  army strength adds to attack
    opposing_army = battle.armies[1-army.armyid]
    priors += np.array([1, 0, 0])*(self.army_power_estimate(army) -
                                   self.army_power_estimate(opposing_army)) 
    m = min(priors)
    if m < 0:
      priors += np.array([1-m, 1-m, 1-m])
      assert min(priors) > 0
    return normalize(priors)

  def expert_yomi_1(self, battle):
    """
    advises playing your own state
    """
    return self.evaluate_state(battle, self.army)

  def _counter(self, strat):
    """
    a strategy is a list
    """
    return np.array(list(strat[2:]) + list(strat[:2]))
  
  def expert_yomi_2(self, battle):
    """
    advises outreading the enemy's state
    """
    return self._counter(self.evaluate_state(battle, battle.armies[1-self.army.armyid]))
  
  def get_formation(self, battle):
    return rps.FormationOrder(random.choice(['A', 'D', 'I']))
  
  def get_final(self, bat):
    player_priors = self.evaluate_state(bat, bat.armies[1-self.armyid])
    bat.battlescreen.yprint("  AI evaluates player (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*player_priors), mode=['huddle'])
    counters = self.expert_yomi_2(bat)
    bat.battlescreen.yprint("  AI counterpicks    (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*counters), mode=['huddle'])
    return rps.FinalOrder(np.random.choice(['A', 'D', 'I'], p=counters))

class RockIntelligence(Intelligence):

  def get_formation(self, battle):
    return rps.FormationOrder('A')

  def get_final(self, battle):
    return rps.FinalOrder('A')

class PaperIntelligence(Intelligence):

  def get_formation(self, battle):
    return rps.FormationOrder('D')

  def get_final(self, battle):
    return rps.FinalOrder('D')

class ScissorsIntelligence(Intelligence):

  def get_formation(self, battle):
    return rps.FormationOrder('I')

  def get_final(self, battle):
    return rps.FinalOrder('I')

INTELLIGENCE_FROM_TYPE = {'INT_AI_NORMAL': ArtificialIntelligence,
                          'INT_PLAYER': PlayerIntelligence,
                          'INT_AI_ROCK': RockIntelligence,
                          'INT_AI_PAPER': PaperIntelligence,
                          'INT_AI_SCISSORS': ScissorsIntelligence,
                          }
