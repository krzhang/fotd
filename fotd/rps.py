WIN = 1
LOSE = 0

BEATS = {'A':'I',
         'D':'A',
         'I':'D'}


FORMATION_ORDERS = {
  'A': {
    "desc": "{ctarget_army} takes an $[1,3]$offensive$[7]$ formation.",
    "desc_bonus": "$[1,3]$A$[7]$ tactics against $[3,3]$indirect$[7]$ orders are $[2,1]$guaranteed$[7]$ on $[1,3]$attack$[7]$.",
    "status": "form_offensive",
    "adj": "offensive",
    "color": "$[1,3]$",
    "physical_offense": 1.0,
    "physical_defense": 1.0,
    "arrow_offense": 1.0,
    "arrow_defense": 1.0,
    "morale_cost":{'A':0, 'D':1, 'I':1}
  },
  "D": {
    "adj": "defensive",
    "color": "$[4,3]$",
    "desc":"{ctarget_army} takes a $[4,3]$defensive$[7]$ formation.",
    "desc_bonus": "$[4,3]$D$[7]$ tactics against $[1,3]$attack$[7]$ orders are $[2,1]$guaranteed$[7]$ on $[4,3]$defense$[7]$.",
    "status": "form_defensive",
    "physical_offense": 0.8,
    "physical_defense": 1.2,
    "arrow_offense": 1.0,
    "arrow_defense": 1.2,
    "morale_cost":{'A':1, 'D':0, 'I':1}
  },
  "I": {
    "adj": "scattered",
    "color": "$[3,3]$",
    "desc":"{ctarget_army} takes a $[3,3]$scattered$[7]$ formation.",
    "desc_bonus": "$[3,3]$I$[7]$ tactics against $[4,3]$defense$[7]$ orders are $[2,1]$guaranteed$[7]$ on $[3,3]$indirect$[7]$ orders.",
    "status": "form_scattered",
    "physical_offense": 1.0,
    "physical_defense": 1.0,
    "arrow_offense": 1.0,
    "arrow_defense": 1.0,
    "morale_cost":{'A':1, 'D':1, 'I':0}
  }
}

FORMATION_ORDER_LIST = ['A', 'D', 'I'] # need an order on the list for consistent IO

class Order():
  def __init__(self, order_str):
    self._str = order_str

  def __eq__(self, other):
    return str(self) == str(other)

  def __str__(self):
    return self._str

class FormationOrder(Order):
  def __init__(self, order_str):
    super().__init__(order_str)
    
  def __repr__(self):
    return "FormationOrder({})".format(self._str)

  def color_abbrev(self):
    return formation_info(self._str, "color") + self._str + "$[7]$"

class FinalOrder(Order):
  def __init__(self, form_str):
    super().__init__(form_str)
    
  def __repr__(self):
    return "FinalOrder({})".format(self._str)

  def color_abbrev(self):
    return order_info(self._str, "color") + self._str + "$[7]$"
  
FINAL_ORDERS = {
  "A": {
    "desc": "{ctarget_army} $[1,3]$marches$[7]$!",
    "yomi_bonus": "against $[3,3]$indirect$[7]$ orders: physical attacks up, $[1,3]$A$[7]$ tactics $[2]$enabled$[7]$!",
    "commitment_bonus": "$[1,3]$A$[7]$ tactics against $[3,3]$indirect$[7]$ orders are $[2,1]$guaranteed$[7]$!",
    "color": "$[1,3]$",
    "color_bulbed": "$[1,3]$",    
    "event": "attack_order",
    "noun": "attack",
    "verb": "marches",
    },
  "D": {
    "desc": "{ctarget_army} $[4,3]$fortifies$[7]$!",
    "yomi_bonus": "against $[1,3]$attack$[7]$ orders: defense strength up, $[4,3]$D$[7]$ tactics $[2]$enabled$[7]$!",
    "commitment_bonus": "$[4,3]$D$[7]$ tactics against $[1,3]$attack$[7]$ orders are $[2,1]$guaranteed$[7]$!",
    "color": "$[4,3]$",
    "color_bulbed": "$[4,3]$",    
    "event": "defense_order",
    "noun": "defense",
    "verb": "fortifies",
  },
  "I": {
    "desc": "{ctarget_army} $[4,3]$scatters$[7]$!",
    "yomi_bonus": "against $[4,3]$defensive$[7]$ orders: arrow strength up, $[3,3]$I$[7]$ tactics $[2]$enabled$[7]$!",
    "commitment_bonus": "$[3,3]$I$[7]$ tactics against $[4,3]$defensive$[7]$ orders are $[2,1]$guaranteed$[7]$!",
    "color": "$[3,3]$",
    "color_bulbed": "$[3,3]$",    
    "event": "indirect_order",
    "noun": "skullduggery",
    "verb": "scatters",
   }
}

FINAL_ORDER_LIST = ['A', 'D', 'I'] # keeping the possibility that this list is different

def beats(t1, t2):
  return BEATS[str(t1)] == str(t2)

def order_to_event(order):
  return FINAL_ORDERS[str(order)]["event"]

def formation_info(form, info_key):
  return FORMATION_ORDERS[form][info_key]

def order_info(order, info_key):
  return FINAL_ORDERS[str(order)][info_key]

def orders_to_winning_armyid(orders):
  """
  Given a tuple (x,y) of orders, returns the Yomi status, which means a winner (0 or 1) if either
  won, or -1 otherwise.
  """
  x,y = orders
  if str(x) == str(y):
    return -1
  if BEATS[str(x)] == str(y):
    return 0
  else:
    assert BEATS[str(y)] == str(x)
    return 1
