import logging

import textutils
from colors import Colors
from character import Character
from army import Unit, Army
import battle
import intelligence
import events
import random
import status
import sys
# power/intel/pol/cha/coolness/bravery

SKILLS_IMPLEMENTED = ["counter_arrow",
                      "chu_ko_nu",
                      "panic_tactic",
                      "fire_tactic",
                      "jeer",
                      "lure",
                      "trymode",
                      "water_tactic"]

def test_char(name, style, power, intel, pol, cha, cool, brave, skills):
  return Character(name, style, power, intel, pol, cha, cool, brave,
                   [s for s in skills if s in SKILLS_IMPLEMENTED])

Yan = test_char("Zhang Yan", "Yellow Lightning",
  71, 80, 74, 60, 5, 4,  ["pincer_specialist", "perfect_defense", "water_tactic", "empty_castle_tactic", "drop_rocks", "counter_tactic", "lure"])

Jing = test_char("Jing Chan", "Purge",
  55, 70, 90, 85, 4, 5, ["trymode", "counter_arrow", "fire_tactic", "chu_ko_nu"]) #items  
Jing.equip("FLAME_BLADE")

Yoyo = test_char("You Zhou", "Caffeinator",
  31, 90, 63, 21, 4, 2,["cheer", "attack_supplies", "fire_tactic", "panic_tactic", "chaos"]) 

Han = test_char("Han Xu", "Finalmente",
  90, 85, 12, 24, 2, 6,  ["sneak_attack", "dash", "jeer", "chaos_arrow", "headhunter"])

LiuBei = test_char("Liu Bei", "",
  70, 81, 89, 100, 4, 5,["cheer", "recruit_specialist"]) #items  

GuanYu = test_char("Guan Yu", "War God",
  98, 80, 53, 92, 6, 7, ["water_tactic", "study", "valor", "jeer"])
GuanYu.equip("BLACK_DRAGON")
GuanYu.equip("RED_HARE")

ZhangFei = test_char("Zhang Fei", "",
  99, 18, 13, 22, 1, 7, ["panic_tactic", "charge", "jeer"])
ZhangFei.equip("SNAKE_SPEAR")

HuangZhong = test_char("Huang Zhong", "",
  90, 51, 42, 64, 4, 7, ["counter_arrow", "chaos_arrow", "fire_arrow"])

Jeanne = test_char("Jeanne D'Arc", Colors.RED + "Rose" + Colors.ENDC + " of Versailles",
  85, 85, 85, 85, 4, 5, ["lure", "spy", "invent", "trade", "charge", "zeal", "critic", "wealth", "chaos"])

Grant = test_char("Ulysses S. Grant", "",
  91, 51, 28, 62, 4, 4, ["invent", "rally", "jeer", "drop_rocks", "perfect_defense"])

Wyatt = test_char("Wyatt Earp", "",
  97, 83, 57, 80, 5, 7, ["valor", "charge", "duel", "dash", "navy", "cheer", "jeer"])

# need to fix stats
CaoCao = test_char("Cao Cao", "The Usurper",
  82, 93, 92, 97, 6, 5, ["attack_supplies", "sneak_attack", "spy", "reversal", "aid", "scout", "dash", "repair", "riot", "rumor", "flood", "rally", "jeer", "sap", "zeal"])
CaoCao.equip("SWORD_OF_HEAVEN") # +10
CaoCao.equip("SWORD_OF_LIGHT") # +10
CaoCao.equip("MENG_DE_MANUAL") # +3 Skill:reversal
CaoCao.equip("SHADOW_RUNNER")

ZhugeLiang = test_char("Zhuge Liang", "The Sleeping Dragon",
  78, 100, 98, 85, 7, 3,["chu_ko_nu", "fire_tactic", "change_weather", "empty_castle_tactic", "counter_tactic", "chaos", "chart", "flood", "wile", "rumor", "reversal"]) #items  
ZhugeLiang.equip("24_WAR_MANUALS") # int+8 skill:invent
ZhugeLiang.equip("SLEEVE_DARTS")

Einstein = test_char("Albert Einstein", "Eureka",
  4, 100, 83, 70, 5, 1,["plan", "rumor", "sage", "harass", "chu_ko_nu", "siege"]) #items  
# moderation / analytic

YuanShu = test_char("Yuan Shu", "The Usurper",
                    65,65,16,44,4,4, ["fame", "connections", "debate", "siege", "weapons"])

# idea: can have godlike skills that are given early game to particular generals
# such as these

LuBu = test_char("Lu Bu", "The Unmatched",
     100, 38, 13, 40, 1,7, ["avatar"]) # do 4X damage, then do 1.5X damage ignoring defense

ZhouYu= test_char("Zhou Yu", "The Dandy of Zhou",
       71, 96, 97, 86, 2, 5, ["god_of_fire"])

PangTong = test_char("Pang Tong", "The Young Phoenix",
         34, 97, 78, 85, 4, 4, ["chain_tactics"])

LuMeng = test_char("Lu Meng", "",
       81,89,91,78,4,4,["attack_heart"]) # basically vampirism

GuanYinPing = test_char("Guan Yinping", "",
            82, 52, 56, 78, 2, 6, ["escape_route"]) # daughter of Guan Yu

# add: CaoRen + stonewall/iron wall

def army_mysticsoft(armyid, color, aitype):
  return Army("Mysticsoft", [Unit(Yan, 20, 8),
                             Unit(Jing, 16, 12),
                             Unit(Yoyo, 12, 20),
                             Unit(Han, 18, 8)],
              armyid, color, aitype)

def army_shu(armyid, aitype):
  return Army("Shu",[Unit(LiuBei, 20, 12),
                     Unit(GuanYu, 14, 12),
                     Unit(ZhangFei, 14, 4)],
              armyid, color, aitype)

def army_unknown(armyid, color, aitype):
  return Army("Enemy Unknown", random.sample(
    [Unit(LiuBei, 20, 12),
     Unit(GuanYu, 20, 12),
     Unit(ZhangFei, 20, 4),
     Unit(HuangZhong, 20, 10),
     Unit(Jeanne, 20, 10),
     Unit(Grant, 20, 10),
     Unit(CaoCao, 20, 10),
     Unit(ZhugeLiang, 20, 10),
     Unit(Einstein, 20, 10),
     Unit(YuanShu, 20, 10),
     Unit(LuBu, 20, 10),
     Unit(ZhouYu, 20, 10),
     Unit(PangTong, 20, 10),
     Unit(LuMeng, 20, 10),
     Unit(GuanYinPing, 20, 10),
     Unit(Wyatt, 20, 18)],                
    4), armyid, color, aitype)

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
      
link_data_funcs()

def test(debug=False, resize=False, two_players=False):
  textutils.SHOW_DEBUG = debug
  if two_players:
    second_intelligence = "INT_PLAYER"
  else:
    second_intelligence = "INT_AI"
  army0 = army_mysticsoft(0, Colors.BLUE, "INT_PLAYER")
  army1 = army_unknown(1, Colors.RED, second_intelligence)
  if resize:
    print ("\x1b[8;24;80t")
    # print ("\x1b[8;{};80t".format(textutils.BATTLE_SCREEN.max_screen_len))
  bat = battle.Battle(army0, army1)
  graphics.Screen.wrapper(graphics.battle_screen, catch_interrupt = True, arguments=[bat])
  
  while(True):
    bat.take_turn()
    if bat.win_army() != None:
      sys.exit(0)
      
if __name__ == "__main__":
  test(resize=True)
