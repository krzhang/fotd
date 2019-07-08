# import textutils
import numpy as np
import skills
from textutils import yinput_battle_order, yprint
from mathutils import normalize

def get_player_order(battle, armyid):
  return yinput_battle_order("Input orders for army {}(A/D/I):".format(armyid))
    
def get_AI_order(battle, armyid):
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
  yprint("  AI predicts player (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*newpriors))
  counters = np.array(list(newpriors[2:]) + list(newpriors[:2]))
  yprint("  AI counterpicks    (A/D/I): {:4.3f}/{:4.3f}/{:4.3f}".format(*counters))
  return np.random.choice(["A", "D", "I"], p=counters)    

def get_order(battle, int_type, armyid):
  if int_type == 'PLAYER_ARMY':
    return get_player_order(battle, armyid)
  else:
    assert int_type == 'AI_ARMY'
    return get_AI_order(battle, armyid)
