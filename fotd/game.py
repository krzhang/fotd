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

# power/intel/pol/cha/coolness/bravery

SKILLS_IMPLEMENTED = ["counter_arrow",
                      "chu_ko_nu",
                      "panic_skill",
                      "fire_skill",
                      "jeer",
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
HAN_SKILLS = ["sneak_attack", "dash", "jeer", "chaos_arrow", "headhunter"]

PC_ATTRS = [
  ("Zhang Yan", "$[3$]Yellow$[7$] Lightning", 71, 80, 74, 60, 5, 4, YAN_SKILLS),
  ("Jing Chan", "Purge", 55, 70, 90, 85, 4, 5, JING_SKILLS),
  ("Zhou You", "Caffeinator", 31, 90, 63, 21, 4, 2, YOYO_SKILLS),
  ("Han Xu", "Finalmente", 90, 85, 12, 24, 2, 6, HAN_SKILLS)]

BIZARRO_ATTRS = [
  ("Ghanz Nagy", "$[4$]Blue$[7$] Thunder", 71, 80, 74, 60, 5, 4, YAN_SKILLS),
  ("Bling Chan", "Vomit", 55, 70, 90, 85, 4, 5, JING_SKILLS),
  ("You Zhou", "Seal Clubber", 31, 90, 63, 21, 4, 2, YOYO_SKILLS),
  ("Xu Han", "WNBA MVP", 90, 85, 12, 24, 2, 6, HAN_SKILLS)]

OTHER_ATTRS = [
  ("Liu Bei", "", 70, 81, 89, 100, 4, 5,
   ["cheer", "recruit_specialist"]), 
  ("Guan Yu", "War God", 98, 80, 53, 92, 6, 7,
   ["water_skill", "study", "valor", "jeer"]),
  ("Zhang Fei", "", 99, 18, 13, 22, 1, 7,
   ["panic_skill", "charge", "jeer"]),
  ("Huang Zhong", "", 90, 51, 42, 64, 4, 7,
   ["counter_arrow", "chaos_arrow", "fire_arrow"]),
  ("Jeanne D'Arc", "The $[1$]Rose$[7$] of Versailles", 85, 85, 85, 85, 4, 5,
   ["lure_skill", "spy", "invent", "trade", "charge", "zeal", "critic", "wealth", "chaos"]),
  ("Ulysses S. Grant", "", 91, 51, 28, 62, 4, 4,
   ["invent", "rally", "jeer", "drop_rocks", "perfect_defense"]),
  ("Wyatt Earp", "", 97, 83, 57, 80, 5, 7,
   ["valor", "charge", "duel", "dash", "navy", "cheer", "jeer"]),
  # need to fix stats
  ("Cao Cao", "The Usurper", 82, 93, 92, 97, 6, 5,
   ["attack_supplies", "sneak_attack", "spy", "reversal", "aid", "scout", "dash", "repair", "riot", "rumor", "flood", "rally", "jeer", "sap", "zeal"]),
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

PC_UNITS = [Unit(test_char(*args), 20, 10) for args in PC_ATTRS]
BIZARRO_UNITS = [Unit(test_char(*args), 20, 10) for args in BIZARRO_ATTRS]
OTHER_UNITS = [Unit(test_char(*args), 20, 10) for args in BIZARRO_ATTRS + OTHER_ATTRS]

def army_mysticsoft(armyid, color, aitype):
  return Army("Mysticsoft", PC_UNITS, armyid, color, aitype, 7)

def army_bizarro(armyid, color, aitype):
  return Army("Mystic$oft", BIZARRO_UNITS, armyid, color, aitype, 7)

def army_unknown(armyid, color, aitype):
  return Army("Enemy Unknown", random.sample(OTHER_UNITS, 4), armyid, color, aitype, 7)

def link_data_funcs():
  """ A round of processing after getting the text data, to create links to actual functions """
  # first, every event has an actual func
  # so we set EVENTS['burn']['func'] to the actual function 'burn' inside events
  EVENTS = events.EVENTS
  STATUSES = status.STATUSES
  for ev in EVENTS:
    EVENTS[ev]["func"] = getattr(events, ev)
  # second, STATUSES[stat_str][func_name+'func'] will contain a legitimate function
  # Example: if STATUSES['burn'] has 'eot': 'panic_eot', it will now contain an actual function 
  #   named that
  for st in STATUSES:
    for func_type in ["eot", "bot"]:
      if func_type in STATUSES[st]:
        STATUSES[st][func_type+'_func'] = getattr(events, STATUSES[st][func_type][0])

# link_data_funcs()

def play(armies, debug=False, resize=False,
         first_intelligence="INT_PLAYER",
         second_intelligence="INT_AI_NORMAL"):
  if resize:
    print("\x1b[8;24;80t")
    # print ("\x1b[8;{};80t".format(textutils.BATTLE_SCREEN.max_screen_len))
  automated = (first_intelligence != 'INT_PLAYER') and (second_intelligence != 'INT_PLAYER')  
  bat = battle.Battle(armies[0], armies[1], debug_mode=debug, automated=automated)
  # graphics.Screen.wrapper(graphics.battle_screen, catch_interrupt = True, arguments=[bat])
  while(True):
    bat.take_turn()
    losers = bat.losing_status()
    for l in [0, 1]:
      if losers[l]:
        bat.battlescreen.yprint("{} is destroyed!".format(textutils.disp_army(armies[l])))
    if any(losers):
      bat.battlescreen.pause_and_display(pause_str="The battle ends...")
      return 0

def test(debug=False, resize=False,
         first_intelligence="INT_PLAYER",
         second_intelligence="INT_AI_NORMAL"):
  armies = [army_mysticsoft(0, Colours.CYAN, first_intelligence),
            army_bizarro(1, Colours.MAGENTA, second_intelligence)]
  return play(armies, debug, resize, first_intelligence, second_intelligence)
   
if __name__ == "__main__":
  test(resize=True)
