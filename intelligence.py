import numpy as np
import random
import skills
from mathutils import normalize

class Intelligence(object):
  def __init__(self):
    # TODOD: write this later
    pass

  def get_formation(battle, armyid):
    pass

  def get_order(battle, armyid):
    pass

  
class PlayerIntelligence(Intelligence):

  def get_formation(battle, armyid):
    return battle.battlescreen.input_battle_formation(armyid)
  
  def get_order(battle, armyid):
    return battle.battlescreen.input_battle_order(armyid)

class ArtificialIntelligence(Intelligence):

  def get_formation(battle, armyid):
    return random.choice(['O', 'D'])
  
  def get_order(battle, armyid):
  # 2 paths: RPS and story-driven soul reading
    parmy = battle.armies[1-armyid].present_units()
    priors = np.array([10,10,10])
    for unit in parmy:
      for sk in unit.character.skills:
        skstr = sk.skill_str
        if skstr in skills.SKILLS:
          priors += np.array(skills.SKILLS[skstr]["ai_eval"])
  # adjusting for size
        # import pdb; pdb.set_trace()
    priors += np.array([1,0,0])*(battle.armies[1-armyid].str_estimate() -
                battle.armies[armyid].str_estimate())
  # TODO: adjusting for battlefield conditions
    m = min(priors)
    if m < 0:
      priors += np.array([1-m, 1-m, 1-m])
      assert min(priors) > 0
    newpriors = normalize(priors)
    battle.yprint("  AI predicts player (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*newpriors))
    counters = np.array(list(newpriors[2:]) + list(newpriors[:2]))
    battle.yprint("  AI counterpicks    (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*counters))
    return np.random.choice(["A", "D", "I"], p=counters)    

class RockIntelligence(Intelligence):

  def get_formation(battle, armyid):
    return 'O'

  def get_order(battle, armyid):
    return 'A'

  
INTELLIGENCE_FROM_TYPE = {'INT_AI_NORMAL': ArtificialIntelligence,
                          'INT_PLAYER': PlayerIntelligence,
                          'INT_AI_ROCK': RockIntelligence}
    
