import random

class Unit(object):
  def __init__(self, name, size, speed):
    self.name = name
    self.size = size
    self.speed = speed
    
  def virtual_unit(self):
    return Unit(self.name+" Fortification", self.size, self.speed)

  def is_alive(self):
    return self.size > 0

POSITIONS_0 = ['A', 'B', 'C']
POSITIONS_1 = ['D', 'E', 'F']
FIELD_POSITIONS = POSITIONS_0 + POSITIONS_1 + ['X', 'Y']
PLAYER_ARMY = 0
AI_ARMY = 1

class Army(object):
  def __init__(self, name, units):
    self.name = name
    self.units = units

  def is_alive(self):
    return any(self.units, lambda x: x.size > 0)

  def total_size(self):
    return sum([s.size for s in self.units])
  
class Game(object):
  def __init__(self, army1, army2):
    self.armies = [army1, army2]
    self.positions = {p:[] for p in POSITIONS_0 + POSITIONS_1}
    self.morale_diff = 0

  def pos_rice(self, pos):
    if pos == 'X':
      return 0
    elif pos == 'Y':
      return 1
    else:
      return None

  def p2a(self, pos):
    if pos in POSITIONS_0:
      army = 0
    else:
      army = 1
    return army
    
  def p2u(self, pos):
    if pos in POSITIONS_0:
      army = 0
      p = POSITIONS_0
    else:
      army = 1
      p = POSITIONS_1
    # print("%d, %s, %s" % (army, p, pos))
    myindex = p.index(pos)
    return (army, self.armies[army].units[myindex])
    
  def gen_player_orders(self):
    return [(p, p) for p in POSITIONS_0]

  def gen_AI_orders(self):
    choices = POSITIONS_0 + POSITIONS_1
    choices += ['X', 'X', 'Y', 'Y']
    return [(p, random.choice(choices)) for p in POSITIONS_1]

  def display_state(self, player_orders):
    print("===========================================================")
    for i in [0,1]:
      if i == 0:
        ps = POSITIONS_0
        rice = 'X'
      else:
        ps = POSITIONS_1
        rice = 'Y'
      print("Army %d:" % i)
      for j,u in enumerate(self.armies[i].units):
        print("  %s: %s (size: %d, speed: %d)" % (ps[j], u.name, u.size, u.speed))
        if i == 0:
          pdict = dict(player_orders)
          print("    -> %s" % pdict[ps[j]])
      print("  %s: supplies" % rice)
    print("Morale Differential: %d" % self.morale_diff)
    print("===========================================================")
    return

  def legal_order(self, order):
    if len(order) != 2:
      return False
    return order[0] in POSITIONS_0 and order[1] in FIELD_POSITIONS

  def position_update(self, pos_state, pos, new_army, new_unit):
    # pos_state is a list of 2 tuples
    print("  %s arrived at %s" % (new_unit.name, pos)) 
    new_state = [pos_state[0], pos_state[1]]
    if pos_state == [[],[]]:
      # in position; make virtual army
      new_state[new_army] = [new_unit.virtual_unit()]
      print("  %s took first position; set up %d fortifications at %s" % (new_unit.name, new_unit.size, pos))
      riceowner = self.pos_rice(pos)
      if riceowner is not None:
        if new_army == riceowner:
          print("  %s is defending supplies." % new_unit.name)
        else:
          damage = self.armies[1-new_army].total_size()
          print("  %s raided supplies! Army %d loses %d morale!" %
                (new_unit.name, 1-new_army, damage))
          self.morale_diff += ([damage,-damage])[new_army]
    new_state[new_army].append(new_unit)
    return new_state
  
  def win_army(self):
    for i in [0, 1]:
      if not self.armies[i].is_alive:
        return 1-i
    return None

  def execute_position(self, pos, field_state):    
    owner = self.p2a(pos)
    riceowner = self.pos_rice(pos)
    damagedice = [[], []]
    for i in [0,1]:
      for u in field_state[i]:
        print("  %s is present with %d force" % (u.name, u.size))
        damagedice[i] += u.size*[u]
    damagedice_final = [damagedice[0].copy(), damagedice[1].copy()]
    dicecount = [len(damagedice[0]), len(damagedice[1])]
    dicetotal = dicecount[0] + dicecount[1]
    if dicetotal == 0:
      return
    if dicecount[owner] == 0:
      if riceowner is None:
        print("  Artful dodge! Army %d loses %d morale due to missed attack" % (1-owner, 1))
        self.morale_diff += ([1,-1])[owner]
    elif dicecount[1-owner] == 0:
      if riceowner is None:
        print("  Wasted defense! Army %d loses %d morale due to defending needlessly" % (owner, 1))
        self.morale_diff += ([-1,1])[owner]
    else:
      print("  Strength %d vs %d:" % (dicecount[0], dicecount[1]))
      for i in [0,1]:
        damage = int(random.random()*dicecount[i]*dicecount[i]/dicetotal)
        if damage >= dicecount[1-i]:
          print("    Army %d is annhilated at %s!" % (1-i, pos))
          damage = dicecount[1-i]
        print("    Army %d did %d damage at %s!" % (i, damage, pos))
        random.shuffle(damagedice[1-i])
        for d in range(damage):
          u = damagedice[1-i].pop()
          print("      %s took 1 damage!" % u.name)
          u.size -= 1        
    
  def execute(self, orders, AI_orders):
    field_state = {p:[[], []] for p in FIELD_POSITIONS}
    global_orders = []
    for x,y in orders + AI_orders:
      army, unit = self.p2u(x)
      if unit.is_alive():
        speed = unit.speed
        if x == y:
          # speed bonuses
          speed += 5
        final_speed = speed + random.choice([-3,-2,-1,0,1,2,3])
        global_orders.append((x,y, final_speed))
    global_orders.sort(key=lambda x: x[2], reverse=True)
    print("==============================================")
    print("Resolving Movement")
    print("==============================================")    
    for o in global_orders:
      army, unit = self.p2u(o[0])
      print("Resolving %s -> %s with speed %f" % (o[0], o[1], o[2]))
      field_state[o[1]] = self.position_update(field_state[o[1]], o[1], army, unit)
    print("==============================================")
    print("Resolving Battles")
    print("==============================================")    
    for p in FIELD_POSITIONS:
      print("Resolving position %s" % p)
      self.execute_position(p, field_state[p])
      
def army_mysticsoft():
  Yan = Unit('Zhang Yan', 4, 2)
  Jing = Unit('Chan Jing', 3, 3)
  Yoyo = Unit('Zhou You', 2, 5)
  return Army("Mysticsoft", [Yan, Jing, Yoyo])

def army_ro3k():
  LB = Unit('Liu Bei', 3, 3)
  GY = Unit('Guan Yu', 4, 3)
  ZF = Unit('Zhang Fei', 5, 1)
  return Army("Three Kingdoms", [LB, GY, ZF])

tarmy1 = army_mysticsoft()
tarmy2 = army_ro3k()

def play():
  game = Game(tarmy1, tarmy2)
  while(True):
    player_orders = game.gen_player_orders()
    AI_orders = game.gen_AI_orders()
    while(True):
      # get player orders in this loop
      game.display_state(player_orders)
      order = input("Input orders; e.g. 'AD'; 'X' to execute:")
      if order == 'X':
        game.execute(player_orders, AI_orders)
        if game.win_army() != None:
          print("Player %d wins!" % game.win_army())
          return
      elif game.legal_order(order):
        pdict = dict(player_orders)
        pdict[order[0]] = order[1]
        player_orders = list(pdict.items())
        # print(player_orders)
      else:
        print("Illegal order.")
