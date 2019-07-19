import random

import numpy as np
import nashpy
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

  def formation_to_priors(self, formation, opp_formation):
    if not formation:
      return np.array([0,0,0])
    else:
      if str(formation) == 'A':
        base_vec = np.array([1,0,0])
      elif str(formation) == 'D':
        base_vec = np.array([0,1,0])
      elif str(formation) == 'I':
        base_vec = np.array([0,0,1])
      if rps.BEATS[str(formation)] == str(opp_formation):
        base_vec *= 160
      elif str(formation) == str(opp_formation):
        base_vec *= 80
      else:
        base_vec *= 20
      return base_vec

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
    priors += self.formation_to_priors(army.formation, opposing_army.formation)
    return priors

  
  def expert_commitment(self, battle):
    """
    advises playing your own state
    """
    formation = self.army.formation
    opp_formation = battle.armies[1-self.army.armyid].formation
    if not formation:
      return np.array([0,0,0])
    else:
      if str(formation) == 'A':
        base_vec = np.array([1,0,0])
      elif str(formation) == 'D':
        base_vec = np.array([0,1,0])
      elif str(formation) == 'I':
        base_vec = np.array([0,0,1])
      if rps.BEATS[str(formation)] == str(opp_formation):
        base_vec *= 80
      elif str(formation) == str(opp_formation):
        base_vec *= 40
      else:
        base_vec *= 20
      return base_vec
    
    priors = self.evaluate_state(battle, self.army)
    battle.battlescreen.yprint("AI uses yomi 1", mode=['huddle'])
    battle.battlescreen.yprint("AI evaluates own strength (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*priors), mode=['huddle'])
    return priors

  def expert_yomi_1(self, battle):
    """
    advises playing your own state
    """
    priors = self.evaluate_state(battle, self.army)
    battle.battlescreen.yprint("AI uses yomi 1", mode=['huddle'])
    battle.battlescreen.yprint("AI evaluates own strength (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*priors), mode=['huddle'])
    return priors
  
  def expert_yomi_2(self, bat):
    """
    advises outreading the enemy's state
    """
    bat.battlescreen.yprint("AI uses yomi 2", mode=['huddle'])
    player_priors = self.evaluate_state(bat, bat.armies[1-self.army.armyid])
    bat.battlescreen.yprint("  AI evaluates player's strength (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*player_priors), mode=['huddle'])
    counters = counter_strat(player_priors)
    bat.battlescreen.yprint("  AI counterpicks    (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*counters), mode=['huddle'])
    return counters

  def expert_yomi_3(self, bat):
    """
    advises outreading opponent who is reading you
    """
    self_priors_to_enemy = self.evaluate_state(bat, self.army) # eventually disguise; right now info is leaking
    bat.battlescreen.yprint("AI uses yomi 3", mode=['huddle'])
    bat.battlescreen.yprint("  AI evaluates player evaluating AI (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*self_priors_to_enemy), mode=['huddle'])
    enemy_counters = counter_strat(self_priors_to_enemy)
    bat.battlescreen.yprint("  AI evaluates player's counterpick (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*enemy_counters), mode=['huddle'])
    counters_to_counters = counter_strat(enemy_counters)
    bat.battlescreen.yprint("  AI counterpick (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*counters_to_counters), mode=['huddle'])
    return counters_to_counters

  def get_formation(self, bat):
    choose_expert = np.random.choice([
      self.expert_yomi_1,
      self.expert_yomi_2,
      self.expert_yomi_3], p=[0.6,0.3,0.1])
    strat = choose_expert(bat)    
    m = min(strat)
    if m < 0:
      strat += np.array([1-m, 1-m, 1-m])
      assert min(strat) > 0
    nstrat =  normalize(strat)
    return rps.FormationOrder(np.random.choice(['A', 'D', 'I'], p=nstrat))

  def get_final(self, bat):
    choose_expert = np.random.choice([
      self.expert_yomi_1,
      self.expert_yomi_2,
      self.expert_yomi_3], p=[0.6,0.3,0.1])
    strat = choose_expert(bat)
    strat += self.expert_commitment(bat)
    m = min(strat)
    if m < 0:
      strat += np.array([1-m, 1-m, 1-m])
      assert min(strat) > 0
    nstrat = normalize(strat)
    return rps.FinalOrder(np.random.choice(['A', 'D', 'I'], p=nstrat))

class NashIntelligence(Intelligence):

  def get_matrix(self, battle):
    matrix = np.array([[0,0,0], [0,0,0],[0,0,0]])
    for i, mystrat in enumerate(['A','D','I']):
      for j, otherstrat in enumerate(['A','D','I']):
        strat_strs = [mystrat, otherstrat]
        tempbattle = battle.imaginary_copy(self.army.armyid)
        init_eval = battle_edge_estimate(tempbattle, 0)  # your army is 0 in this tempbattle
        for k in [0,1]:
          tempbattle.armies[k].order = rps.FinalOrder(strat_strs[k])
        tempbattle.resolve_orders()
        post_eval = battle_edge_estimate(tempbattle, 0)
        matrix[i][j] = post_eval - init_eval
        battle.battlescreen.yprint("{} vs {}: edge {}".format(mystrat, otherstrat, matrix[i][j]), mode=['huddle'])
    return matrix
  
  def get_formation(self, battle):
    return rps.FormationOrder(np.random.choice(['A','D','I']))

  def get_final(self, battle):
    mat = self.get_matrix(battle)
    game = nashpy.game(mat)
    equilibria = game.support_enumeration()
    strat = next(equilibria)
    battle.battlescreen.yprint("Nash equilibria (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*strat), mode=['huddle'])
    return rps.FinalOrder(np.random.choice(['A','D','I']), p=strat)
  
class TrueRandomIntelligence(Intelligence):

  def get_formation(self, battle):
    return rps.FormationOrder(np.random.choice(['A','D','I']))

  def get_final(self, battle):
    return rps.FinalOrder(np.random.choice(['A','D','I']))
  
class RandomIntelligence(Intelligence):

  def __init__(self, army):
    super().__init__(army)
    self.commit = None

  def get_formation(self, battle):
    self.commit = np.random.choice(['A','D','I'])
    return rps.FormationOrder(self.commit)

  def get_final(self, battle):
    return rps.FinalOrder(self.commit)

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

INTELLIGENCE_FROM_TYPE = {'AI_WIP': ArtificialIntelligence,
                          'PLAYER': PlayerIntelligence,
                          'AI_ROCK': RockIntelligence,
                          'AI_PAPER': PaperIntelligence,
                          'AI_SCISSORS': ScissorsIntelligence,
                          'AI_RANDOM': RandomIntelligence,
                          'AI_TRUE_RANDOM': TrueRandomIntelligence,
                          'AI_NASH': NashIntelligence,
                          }

##################################
# Utility functions everyone has #
##################################

def army_power_estimate(army):
  if army.morale == 0:
    return 0
  return sum([u.size for u in army.present_units()], 0) + army.morale*5

def battle_edge_estimate(battle, armyid):
  return army_power_estimate(battle.armies[armyid]) - army_power_estimate(battle.armies[1-armyid])

def counter_strat(strat):
  """
  returns the strategy to counter another strategy, both given as lists
  """
  return np.array(list(strat[2:]) + list(strat[:2]))

