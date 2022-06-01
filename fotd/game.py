import logging

# create logger with 'spam_application'
logger = logging.getLogger("test")
logger.setLevel(logging.DEBUG)

f = logging.FileHandler("test.log")
f.setLevel(logging.DEBUG)
logger.addHandler(f)

# handler = logging.StreamHandler(sys.stdout)
# handler.setLevel(logging.DEBUG)
# logger.addHandler(handler)

from colors import Colours
from character import Character
from army import Unit, Army

import textutils
import battle
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

# Jing.equip("FLAME_BLADE")
# GuanYu.equip("BLACK_DRAGON")
# GuanYu.equip("RED_HARE")
# ZhangFei.equip("SNAKE_SPEAR")
# CaoCao.equip("SWORD_OF_HEAVEN") # +10
# CaoCao.equip("SWORD_OF_LIGHT") # +10
# CaoCao.equip("MENG_DE_MANUAL") # +3 Skill:reversal
# CaoCao.equip("SHADOW_RUNNER")
# ZhugeLiang.equip("24_WAR_MANUALS") # int+8 skill:invent
# ZhugeLiang.equip("SLEEVE_DARTS")

YAN_SKILLS = ["pincer_specialist", "perfect_defense", "water_skill", "empty_castle_skill", "drop_rocks", "counter_skill", "lure_skill"]
JING_SKILLS = ["trymode", "counter_arrow", "fire_skill", "chu_ko_nu"]
YOYO_SKILLS = ["cheer", "attack_supplies", "dash", "fire_skill", "panic_skill", "chaos"]
HAN_SKILLS = ["sneak_attack", "dash", "jeer_skill", "chaos_arrow", "headhunter"]

# power/intel/pol/cha/coolness/bravery
PC_ATTRS = [ # First Name Last Name, since we are from the future
  ("Yan Zhang", "$[3]$Yellow$[7]$ Lightning", 71, 80, 74, 60, 5, 4, YAN_SKILLS),
  ("Jing Chan", "Purge", 55, 70, 90, 85, 4, 5, JING_SKILLS),
  ("You Zhou", "Caffeinator", 31, 90, 63, 21, 4, 2, YOYO_SKILLS),
  ("Han Xu", "Finalmente", 90, 85, 12, 24, 2, 6, HAN_SKILLS)]

BIZARRO_ATTRS = [
  ("Hanz Nagy", "$[4]$Blue$[7]$ Thunder", 71, 80, 74, 60, 5, 4, YAN_SKILLS),
  ("Bling Chan", "Splurge", 55, 70, 90, 85, 4, 5, JING_SKILLS),
  ("Yo Joe", "Seal Clubber", 31, 90, 63, 21, 4, 2, YOYO_SKILLS),
  ("Xu Han", "WNBA", 90, 85, 12, 24, 2, 6, HAN_SKILLS)]

OTHER_ATTRS = [
  ("Liu Bei", "", 70, 81, 89, 100, 4, 5,
   ["cheer", "recruit_specialist"]), 
  ("Guan Yu", "War God", 98, 80, 53, 92, 6, 7,
   ["water_skill", "study", "valor", "jeer_skill"]),
  ("Zhang Fei", "", 99, 18, 13, 22, 1, 7,
   ["panic_skill", "charge", "jeer_skill"]),
  ("Huang Zhong", "", 90, 51, 42, 64, 4, 7,
   ["counter_arrow", "chaos_arrow", "fire_arrow"]),
  ("Jeanne D'Arc", "The $[1]$Rose$[7]$ of Versailles", 85, 85, 85, 85, 4, 5,
   ["lure_skill", "spy", "invent", "trade", "charge", "zeal", "critic", "wealth", "chaos"]),
  ("Ulysses S. Grant", "", 91, 51, 28, 62, 4, 4,
   ["invent", "rally", "jeer_skill", "drop_rocks", "perfect_defense"]),
  ("Wyatt Earp", "", 97, 83, 57, 80, 5, 7,
   ["valor", "charge", "duel", "dash", "navy", "cheer", "jeer_skill"]),
  # need to fix stats
  ("Cao Cao", "The Usurper", 82, 93, 92, 97, 6, 5,
   ["attack_supplies", "sneak_attack", "spy", "reversal", "aid", "scout", "dash", "repair", "riot", "rumor", "flood", "rally", "jeer_skill", "sap", "zeal"]),
  ("Zhuge Liang", "The Sleeping Dragon", 78, 100, 98, 85, 7, 3,
   ["chu_ko_nu", "fire_skill", "change_weather", "empty_castle_skill", "counter_skill", "chaos", "chart", "flood", "wile", "rumor", "reversal"]), #items  
  ("Albert Einstein", "Eureka", 4, 100, 83, 70, 5, 1,
   ["plan", "rumor", "sage", "harass", "chu_ko_nu", "siege"]), # moderation / analytic
  ("Yuan Shu", "The Usurper", 65,65,16,44,4,4,
   ["fame", "connections", "debate", "siege", "weapons"]),
  # idea: can have godlike skills that are given early game to particular generals
  # such as these
  ("Lu Bu", "The Unmatched", 100, 38, 13, 40, 1,7,
   ["avatar_of_war_diety"]), # do 4X damage, then do 1.5X damage ignoring defense
  ("Zhou Yu", "The Dandy of Zhou", 71, 96, 97, 86, 2, 5,
   ["emperor_of_fire"]),
  ("Pang Tong", "The Young Phoenix", 34, 97, 78, 85, 4, 4, ["lure_skill", "chain_skill"]),
  ("Lu Meng", "", 81,89,91,78,4,4,
   ["attack_heart"]), # basically vampirism
  ("Guan Yinping", "", 82, 52, 56, 78, 2, 6,
   ["escape_route"])] # daughter of Guan Yu

# add: CaoRen + stonewall/iron wall

def play(armies, debug=False, resize=False,
         first_intelligence="PLAYER", second_intelligence="AI_NASH_NASH", show_AI=False):
  if resize:
    print("\x1b[8;24;80t")
    # print ("\x1b[8;{};80t".format(textutils.BATTLE_SCREEN.max_screen_len))
  automated = (first_intelligence != 'PLAYER') and (second_intelligence != 'PLAYER')
  bat = battle.Battle(armies[0], armies[1], debug_mode=debug, automated=automated, show_AI=show_AI)
  # graphics.Screen.wrapper(graphics.battle_screen, catch_interrupt = True, arguments=[bat])
  return bat.start_battle()

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
  armies = [army_mysticsoft(0, Colours.CYAN, first_intelligence, num_units),
            army_bizarro(1, Colours.MAGENTA, second_intelligence, num_units)]
  return play(armies, debug, resize, first_intelligence, second_intelligence, show_AI)

def test_duel(debug=False, resize=False,
         first_intelligence="PLAYER",
         second_intelligence="AI_NASH_NASH"):
  armies = [army_mysticsoft(0, Colours.CYAN, first_intelligence),
            army_bizarro(1, Colours.MAGENTA, second_intelligence)]
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
    armies = [army_mysticsoft(0, Colours.CYAN, first_intelligence, num_units, size=sizes[0], morale=morales[0]),
            army_bizarro(1, Colours.MAGENTA, second_intelligence, num_units, size=sizes[1], morale=morales[1])]
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
