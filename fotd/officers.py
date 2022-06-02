"""
Officers for testing purposes.
"""

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
