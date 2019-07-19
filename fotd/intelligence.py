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

  def formation_to_priors(self, formation):
    if not formation:
      return np.array([0,0,0])
    elif str(formation) == 'A':
      return np.array([20,0,0])
    elif str(formation) == 'D':
      return np.array([0,20,0])
    elif str(formation) == 'I':
      return np.array([0,0,20])

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

    # formation adds to attack
    priors += self.formation_to_priors(army.formation)
    m = min(priors)
    if m < 0:
      priors += np.array([1-m, 1-m, 1-m])
      assert min(priors) > 0
    return normalize(priors)

  def expert_yomi_1(self, battle):
    """
    advises playing your own state
    """
    priors = self.evaluate_state(battle, self.army)
    battle.battlescreen.yprint("AI uses yomi 1", mode=['huddle'])
    battle.battlescreen.yprint("AI evaluates own strength (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*priors), mode=['huddle'])
    return 

  def _counter(self, strat):
    """
    a strategy is a list
    """
    return np.array(list(strat[2:]) + list(strat[:2]))
  
  def expert_yomi_2(self, bat):
    """
    advises outreading the enemy's state
    """
    bat.battlescreen.yprint("AI uses yomi 2", mode=['huddle'])
    player_priors = self.evaluate_state(bat, bat.armies[1-self.army.armyid])
    bat.battlescreen.yprint("  AI evaluates player's strength (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*player_priors), mode=['huddle'])
    counters = self._counter(player_priors)
    bat.battlescreen.yprint("  AI counterpicks    (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*counters), mode=['huddle'])
    return counters

  def expert_yomi_3(self, bat):
    """
    advises outreading opponent who is reading you
    """
    self_priors_to_enemy = self.evaluate_state(bat, self.army) # eventually disguise; right now info is leaking
    bat.battlescreen.yprint("AI uses yomi 3", mode=['huddle'])
    bat.battlescreen.yprint("  AI evaluates player evaluating AI (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*self_priors_to_enemy), mode=['huddle'])
    enemy_counters = self._counter(self_priors_to_enemy)
    bat.battlescreen.yprint("  AI evaluates player's counterpick (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*enemy_counters), mode=['huddle'])
    counters_to_counters = self._counter(enemy_counters)
    bat.battlescreen.yprint("  AI counterpick (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*counters_to_counters), mode=['huddle'])
    return counters_to_counters

  def get_formation(self, bat):
    choose_expert = np.random.choice([
      self.expert_yomi_1,
      self.expert_yomi_2,
      self.expert_yomi_3], p=[0.5,0.3,0.2])
    strat = choose_expert(bat)
    return rps.FormationOrder(np.random.choice(['A', 'D', 'I'], p=strat))

  def get_final(self, bat):
    choose_expert = np.random.choice([
      self.expert_yomi_1,
      self.expert_yomi_2,
      self.expert_yomi_3], p=[0.5,0.3,0.2])
    strat = choose_expert(bat)
    return rps.FinalOrder(np.random.choice(['A', 'D', 'I'], p=strat))

class RandomIntelligence(Intelligence):

  def get_formation(self, battle):
    return rps.FormationOrder(np.random.choice(['A','D','I']))

  def get_final(self, battle):
    return rps.FinalOrder(np.random.choice(['A','D','I']))

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
                          'INT_AI_RANDOM': RandomIntelligence,
                          }
