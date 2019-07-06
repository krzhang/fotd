from textutils import Colors, yprint, yinput
from army import Character, Unit, Army
import battle
import events
import random
import status

# power/intel/pol/cha/coolness/bravery

Yan = Character("Zhang Yan", "Yellow Lightning",
  71, 80, 74, 60, 5, 4,  ["pincer_specialist", "perfect_defense", "flood", "empty_castle_tactic", "drop_rocks", "counter_tactic"])

Jing = Character("Jing Chan", "Purge",
  55, 70, 90, 85, 4, 5, ["trymode", "counter_arrow", "fire_tactic", "chu_ko_nu"]) #items  
Jing.equip("FLAME_BLADE")

Yoyo = Character("You Zhou", "Caffeinator",
  31, 90, 63, 21, 4, 2,["cheer", "attack_supplies", "fire_tactic", "panic_tactic", "jeer"]) 

Han = Character("Han Xu", "Finalmente",
  90, 85, 12, 24, 2, 6,  ["sneak_attack", "dash", "jeer", "chaos_arrow", "headhunter"])

LiuBei = Character("Liu Bei", "",
  70, 81, 89, 100, 4, 5,["cheer", "recruit_specialist"]) #items  

GuanYu = Character("Guan Yu", "War God",
  98, 80, 53, 92, 6, 7, ["flood", "study", "valor"])
GuanYu.equip("BLACK_DRAGON")
GuanYu.equip("RED_HARE")

ZhangFei = Character("Zhang Fei", "",
  99, 18, 13, 22, 1, 7, ["panic_tactic", "charge"])
ZhangFei.equip("SNAKE_SPEAR")

HuangZhong = Character("Huang Zhong", "",
  90, 51, 42, 64, 4, 7, ["counter_arrow", "chaos_arrow", "fire_arrow"])

Jeanne = Character("Jeanne D'Arc", Colors.RED + "Rose" + Colors.ENDC + " of Versailles",
  85, 85, 85, 85, 4, 5, ["spy", "invent", "trade", "charge", "zeal", "critic", "wealth"])

Grant = Character("Ulysses S. Grant", "",
  91, 51, 28, 62, 4, 4, ["invent", "rally", "jeer", "drop_rocks", "perfect_defense"])

Wyatt = Character("Wyatt Earp", "",
  97, 83, 57, 80, 5, 7, ["valor", "charge", "duel", "dash", "navy", "cheer", "jeer"])

# need to fix stats
CaoCao = Character("Cao Cao", "The Usurper",
  90, 51, 42, 64, 4, 7, ["attack_supplies", "sneak_attack"])

ZhugeLiang = Character("Zhuge Liang", "The Genius",
  70, 81, 89, 100, 4, 5,["chu_ko_nu", "fire_tactic", "change_weather", "empty_castle_tactic", "counter_tactic"]) #items  

Einstein = Character("Albert Einstein", "Eureka",
  4, 100, 83, 70, 5, 1,["plan", "rumor", "sage", "harass", "volley", "siege"]) #items  
# moderation / analytic

def army_mysticsoft(armyid, color):
  return Army("Mysticsoft", [Unit(Yan, 20, 8),
                             Unit(Jing, 16, 12),
                             Unit(Yoyo, 12, 20),
                             Unit(Han, 18, 8)],
              armyid, color)

def army_shu(armyid):
  return Army("Shu",[Unit(LiuBei, 20, 12),
                     Unit(GuanYu, 14, 12),
                     Unit(ZhangFei, 14, 4)],
              armyid, color)

def army_unknown(armyid, color):
  return Army("Enemy Unknown", random.sample(
    [Unit(LiuBei, 20, 12),
     Unit(GuanYu, 14, 12),
     Unit(ZhangFei, 14, 4),
     Unit(HuangZhong, 14, 10),
     Unit(Jeanne, 20, 10),
     Unit(Grant, 20, 10),
     Unit(CaoCao, 20, 10),
     Unit(ZhugeLiang, 20, 10),
     Unit(Wyatt, 10, 18)],                
    4), armyid, color)

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
bat = battle.Battle(army_mysticsoft(0, Colors.BLUE), army_unknown(1, Colors.RED))
while(True):
  # get player orders in this loop
  bat.init_turn_state()
  while(True):
    bat.display_state()
    order = yinput("Input orders (A/D/I):")
    # order = utils.read_single_keypress()[0]
    if bat.legal_order(order):
      AI_order = bat.gen_AI_order()
      bat.take_turn([order.upper(), AI_order])
      if bat.win_army() != None:
        exit()
      bat.init_turn_state()
    else:
      yprint("Illegal order.")
      
