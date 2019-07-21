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
    opposing_army = army.other_army()
    priors += np.array([1, 0, 0])*(army_power_estimate(army) -
                                   army_power_estimate(opposing_army))
  
    # formation adds to attack
    priors += self.formation_to_priors(army.formation, opposing_army.formation)
    return priors

  
  def expert_commitment(self, battle):
    """
    advises playing your own state
    """
    formation = self.army.formation
    opp_formation = self.army.other_army().formation
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
    battle.battlescreen.yprint("AI uses yomi 1", mode=['AI'])
    battle.battlescreen.yprint("AI evaluates own strength (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*priors), mode=['AI'])
    return priors

  def expert_yomi_1(self, battle):
    """
    advises playing your own state
    """
    priors = self.evaluate_state(battle, self.army)
    battle.battlescreen.yprint("AI uses yomi 1", mode=['AI'])
    battle.battlescreen.yprint("AI evaluates own strength (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*priors), mode=['AI'])
    return priors
  
  def expert_yomi_2(self, bat):
    """
    advises outreading the enemy's state
    """
    bat.battlescreen.yprint("AI uses yomi 2", mode=['AI'])
    player_priors = self.evaluate_state(bat, bat.armies[1-self.army.armyid])
    bat.battlescreen.yprint("  AI evaluates player's strength (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*player_priors), mode=['AI'])
    counters = counter_strat(player_priors)
    bat.battlescreen.yprint("  AI counterpicks    (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*counters), mode=['AI'])
    return counters

  def expert_yomi_3(self, bat):
    """
    advises outreading opponent who is reading you
    """
    self_priors_to_enemy = self.evaluate_state(bat, self.army) # eventually disguise; right now info is leaking
    bat.battlescreen.yprint("AI uses yomi 3", mode=['AI'])
    bat.battlescreen.yprint("  AI evaluates player evaluating AI (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*self_priors_to_enemy), mode=['AI'])
    enemy_counters = counter_strat(self_priors_to_enemy)
    bat.battlescreen.yprint("  AI evaluates player's counterpick (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*enemy_counters), mode=['AI'])
    counters_to_counters = counter_strat(enemy_counters)
    bat.battlescreen.yprint("  AI counterpick (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*counters_to_counters), mode=['AI'])
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

class NashIntelligence(ArtificialIntelligence):

  def get_formation_matrix(self, battle):
    matrix = np.array([[0,0,0], [0,0,0],[0,0,0]])
    for i, strat0 in enumerate(['A','D','I']):
      for j, strat1 in enumerate(['A','D','I']):
        strat_strs = [strat0, strat1]
        for _ in range(3):
          tempbattle = battle.imaginary_copy("AI_RANDOM_COMMITTER")
          for k in [0,1]:
            tempbattle.armies[k].formation = rps.FormationOrder(strat_strs[k])
          init_eval = battle_edge_estimate(tempbattle, 0)
          # simulate the rest of the turn; should get orders and then resolve them
          tempbattle._get_orders()
          tempbattle.resolve_orders()
          post_eval = battle_edge_estimate(tempbattle, 0)
          matrix[i][j] += post_eval - init_eval
        battle.battlescreen.yprint("{} vs {}: edge {}".format(strat0, strat1, matrix[i][j]), mode=['AI'])
    return matrix

  def get_formation(self, battle):
    mat = self.get_formation_matrix(battle)
    rstrats0, rstrats1, _ = williams_solve_old(mat.tolist(), 100)
    strats = [normalize(rstrats0), normalize(rstrats1)]
    strat = strats[self.army.armyid]
    battle.battlescreen.yprint("Beststrats (A/D/I): {:4.3f}/{:4.3f}/{:4.3f} vs {:4.3f}/{:4.3f}/{:4.3f}".format(*(strats[0] + strats[1])), mode=['AI'])
    battle.battlescreen.yprint("Nash equilibria (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*strat), mode=['AI'])
    return rps.FormationOrder(np.random.choice(['A','D','I'], p=strat))
  
  def get_final_matrix(self, battle):
    matrix = np.array([[0,0,0], [0,0,0],[0,0,0]])
    for i, strat0 in enumerate(['A','D','I']):
      for j, strat1 in enumerate(['A','D','I']):
        strat_strs = [strat0, strat1]
        for _ in range(3):
          tempbattle = battle.imaginary_copy("AI_RANDOM_RANDOM")
          for k in [0,1]:
            tempbattle.armies[k].order = rps.FinalOrder(strat_strs[k])
          init_eval = battle_edge_estimate(tempbattle, 0)
          tempbattle.resolve_orders()
          post_eval = battle_edge_estimate(tempbattle, 0)
          matrix[i][j] += post_eval - init_eval
        battle.battlescreen.yprint("{} vs {}: edge {}".format(strat0, strat1, matrix[i][j]), mode=['AI'])
    return matrix
  
  def get_final(self, battle):
    mat = self.get_final_matrix(battle)
    rstrats0, rstrats1, _ = williams_solve_old(mat.tolist(), 100)
    strats = [normalize(rstrats0), normalize(rstrats1)]
    strat = strats[self.army.armyid]
    battle.battlescreen.yprint("Beststrats (A/D/I): {:4.3f}/{:4.3f}/{:4.3f} vs {:4.3f}/{:4.3f}/{:4.3f}".format(*(strats[0] + strats[1])), mode=['AI'])
    battle.battlescreen.yprint("Nash equilibria (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*strat), mode=['AI'])
    # bestvals = [None, None]
    # beststrats = [None, None]
    # for eq in tgame.vertex_enumeration():
    #   val0 = np.matmul(np.matmul(eq[0], tgame.payoff_matrices[0]), np.array([1,1,1]).T)
    #   if not bestvals[0] or val0 > bestvals[0]:
    #     bestvals[0] = val0
    #     beststrats[0] = eq[0]
    #   val1 = np.matmul(np.matmul(np.array([1, 1, 1]), tgame.payoff_matrices[0]), eq[1].T)
    #   if not bestvals[1] or val1 < bestvals[1]:
    #     bestvals[1] = val1
    #     beststrats[1] = eq[1]
    # for i in [0,1]:
    #   if beststrats[i] is None:
    #     beststrats[i] = np.array([1,1,1])
    # strat0 = normalize(beststrats[0])
    # strat1 = normalize(beststrats[1])
    # strat = normalize(beststrats[self.army.armyid])
    # battle.battlescreen.yprint("Beststrats (A/D/I): {:4.3f}/{:4.3f}/{:4.3f} vs {:4.3f}/{:4.3f}/{:4.3f}".format(*(strat0 + strat1)), mode=['AI'])
    # battle.battlescreen.yprint("Nash equilibria (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*strat), mode=['AI'])
    return rps.FinalOrder(np.random.choice(['A','D','I'], p=strat))
  
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
    return rps.FinalOrder(str(self.army.formation))
  
class HeuCommitter(ArtificialIntelligence):

  def __init__(self, army):
    super().__init__(army)
    self.commit = None

  def get_formation(self, battle):
    self.commit = super().get_formation(battle)
    return self.commit

  def get_final(self, battle):
    return rps.FinalOrder(str(self.army.formation))

class NashCommitter(NashIntelligence):

  def get_final(self, battle):
    return rps.FinalOrder(str(self.army.formation))

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

INTELLIGENCE_FROM_TYPE = {'AI_HEU_HEU': ArtificialIntelligence,
                          'PLAYER': PlayerIntelligence,
                          'AI_ROCK': RockIntelligence,
                          'AI_PAPER': PaperIntelligence,
                          'AI_SCISSORS': ScissorsIntelligence,
                          'AI_RANDOM_COMMITTER': RandomIntelligence,
                          'AI_RANDOM_RANDOM': TrueRandomIntelligence,
                          'AI_NASH_NASH': NashIntelligence,
                          'AI_HEU_COMMITTER': HeuCommitter,
                          'AI_NASH_COMMITTER': NashCommitter,
                          }

##################################
# Utility functions everyone has #
##################################

''' 
[Game theory payoff matrix solver « Python recipes « ActiveState Code](http://code.activestate.com/recipes/496825-game-theory-payoff-matrix-solver/)
- changed for numpy

Approximate the strategy oddments for 2 person zero-sum games of perfect information.

Applies the iterative solution method described by J.D. Williams in his classic
book, The Compleat Strategyst, ISBN 0-486-25101-2.   See chapter 5, page 180 for details. '''

from operator import add, neg

def williams_solve(payoff_matrix, iterations=100):
  'Return the oddments (mixed strategy ratios) for a given payoff matrix'
  transpose = payoff_matrix.T
  numrows = len(payoff_matrix)
  numcols = len(transpose)
  row_cum_payoff = np.array([0] * numrows)
  col_cum_payoff = np.array([0] * numcols)
  colpos = range(numcols)
  rowpos = map(neg, range(numrows))
  colcnt = np.array([0] * numcols)
  rowcnt = np.array([0] * numrows)
  active = 0
  for _ in range(iterations):
    rowcnt[active] += 1
    col_cum_payoff = payoff_matrix[active] + col_cum_payoff
    active = min([u for u in zip(col_cum_payoff, colpos)])[1]
    colcnt[active] += 1
    row_cum_payoff += transpose[active]
    active = -max([u for u in zip(row_cum_payoff, rowpos)])[1]
  value_of_game = (max(row_cum_payoff) + min(col_cum_payoff)) / 2.0 / iterations
  return rowcnt, colcnt, value_of_game

def williams_solve_old(payoff_matrix, iterations=100):
  'Return the oddments (mixed strategy ratios) for a given payoff matrix'
  transpose = [u for u in zip(*payoff_matrix)]
  numrows = len(payoff_matrix)
  numcols = len(transpose)
  row_cum_payoff = [0] * numrows
  col_cum_payoff = [0] * numcols
  colpos = [c for c in range(numcols)]
  rowpos = [r for r in map(neg, range(numrows))]
  colcnt = [0] * numcols
  rowcnt = [0] * numrows
  active = 0
  for i in range(iterations):
    rowcnt[active] += 1        
    col_cum_payoff = [t for t in map(add, payoff_matrix[active], col_cum_payoff)]
    active = min([u for u in zip(col_cum_payoff, colpos)])[1]
    colcnt[active] += 1       
    row_cum_payoff = [t for t in map(add, transpose[active], row_cum_payoff)]
    active = -max([u for u in zip(row_cum_payoff, rowpos)])[1]
  value_of_game = (max(row_cum_payoff) + min(col_cum_payoff)) / 2.0 / iterations
  return rowcnt, colcnt, value_of_game
  
def army_power_estimate(army):
  if army.morale == 0:
    return 0
  return sum([u.size for u in army.present_units()], 0) + army.morale*4

def battle_edge_estimate(battle, armyid):
  return army_power_estimate(battle.armies[armyid]) - army_power_estimate(battle.armies[1-armyid])

def counter_strat(strat):
  """
  returns the strategy to counter another strategy, both given as lists
  """
  return np.array(list(strat[2:]) + list(strat[:2]))

