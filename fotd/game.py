import logging
# create logger with 'spam_application'
logger = logging.getLogger("test")
logger.setLevel(logging.INFO)

flog = logging.FileHandler("test.log")
flog.setLevel(logging.DEBUG)
logger.addHandler(flog)

# handler = logging.StreamHandler(sys.stdout)
# handler.setLevel(logging.DEBUG)
# logger.addHandler(handler)

from character import Character
from army import Unit, Army
from colors import YCodes

import battle
import pygameview
# import graphics_asciimatics
import intelligence
import events
import random
import status
import sys


SKILLS_IMPLEMENTED = ["counter_arrow",
                      "chu_ko_nu",
                      "panic_skill",
                      "fire_skill",
                      "jeer_skill",
                      "lure_skill",
                      "trymode",
                      "water_skill"]

def test_char(name, style, power, intel, pol, cha, cool, brave, skills):
  return Character(name, style, power, intel, pol, cha, cool, brave,
                   [s for s in skills if s in SKILLS_IMPLEMENTED])

from officers import YAN_SKILLS, JING_SKILLS, YOYO_SKILLS, HAN_SKILLS, PC_ATTRS, BIZARRO_ATTRS, OTHER_ATTRS


# def play(map_file):
#     if map_file is None:
#         main_menu()
#     else:
#         s.load_map(map_file)

#     while True:
#         actual_game()
#         main_menu()
        
def play(armies, debug=False, resize=False,
         first_intelligence="PLAYER", second_intelligence="AI_NASH_NASH", show_AI=False):
  if resize:
    print("\x1b[8;24;80t")
  
  automated = (first_intelligence != 'PLAYER') and (second_intelligence != 'PLAYER')
  bat = battle.Battle(armies[0], armies[1],
                      debug_mode=debug, automated=automated,
                      show_AI=show_AI)
  print("Did we get here?")
  bat.start_battle()
  battlescreen = pygameview.PGBattleView(bat, 0, automated=automated, show_AI=show_AI)
  bat.battlescreen = battlescreen
  battlescreen.new()

  # return bat.start_battle()  # eventually need to return values
  return None
 
def army_mysticsoft(armyid, color, aitype, num=4,morale=7,size=20):
  PC_UNITS = [Unit(test_char(*args), size, 10) for args in PC_ATTRS]
  return Army("Mysticsoft", PC_UNITS[:num], armyid, color, aitype, morale)

def army_bizarro(armyid, color, aitype, num=4,morale=7,size=20):
  BIZARRO_UNITS = [Unit(test_char(*args), size, 10) for args in BIZARRO_ATTRS]
  return Army("Mysterioussoft", BIZARRO_UNITS[:num], armyid, color, aitype, morale)

def army_unknown(armyid, color, aitype, num=4,morale=7,size=20):
  OTHER_UNITS = [Unit(test_char(*args), size, 10) for args in BIZARRO_ATTRS + OTHER_ATTRS]
  return Army("Enemy Unknown", random.sample(OTHER_UNITS, 4)[:num], armyid, color, aitype, morale)
    
def test(debug=False, resize=False, first_intelligence="PLAYER",
         second_intelligence="AI_NASH_NASH", num_units=4, show_AI=False):
  armies = [army_mysticsoft(0, YCodes.CYAN, first_intelligence, num_units),
            army_bizarro(1, YCodes.MAGENTA, second_intelligence, num_units)]
  return play(armies, debug, resize, first_intelligence, second_intelligence, show_AI)

def test_duel(debug=False, resize=False,
         first_intelligence="PLAYER",
         second_intelligence="AI_NASH_NASH"):
  armies = [army_mysticsoft(0, YCodes.CYAN, first_intelligence),
            army_bizarro(1, YCodes.MAGENTA, second_intelligence)]
  automated = (first_intelligence != 'PLAYER') and (second_intelligence != 'PLAYER')
  bat = battle.Battle(armies[0], armies[1], debug_mode=debug, automated=automated)
  armies[0].units[0].health = 100
  armies[1].units[1].health = 100  
  import events
  import contexts
  events.duel_accepted(bat, contexts.Context({
    'csource':armies[0].units[0],
    'ctarget':armies[1].units[1]}), bat.battlescreen, bat.narrator)
  return 0

def test_AI(debug=False, resize=False, first_intelligence="AI_NASH_NASH",
            second_intelligence="AI_RANDOM",
            morales = (7,7),
            sizes = (20, 20),
            num_units=4, trials=100):
  final_results = [0, 0]
  for _ in range(trials):
    armies = [army_mysticsoft(0, YCodes.CYAN, first_intelligence, num_units, size=sizes[0], morale=morales[0]),
            army_bizarro(1, YCodes.MAGENTA, second_intelligence, num_units, size=sizes[1], morale=morales[1])]
    bat = battle.Battle(armies[0], armies[1], debug_mode=False, automated=True)
    results = bat.start_battle()
    for j in [0,1]:
      if results[j]:
        final_results[j] += 1
  return final_results

def test_AI_all(debug=False, resize=False, trials=100):
  ai_strs = ['AI_ROCK',
             'AI_PAPER',
             'AI_SCISSORS',
             'AI_RANDOM_COMMITTER',
             'AI_RANDOM_RANDOM',
             'AI_NASH_COMMITTER',
             'AI_NASH_NASH']
  for i in ai_strs:
    for j in ai_strs:
      if i == j and i == "AI_PAPER":
        continue
      results = test_AI(first_intelligence=i, second_intelligence=j, trials=trials)
      print("{} vs {}: {}".format(i, j, results))

if __name__ == "__main__":
  test(resize=True)
