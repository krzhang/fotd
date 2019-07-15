WIN = 1
LOSE = 0

BEATS = {'A':'I',
         'D':'A',
         'I':'D'}


FORMATION_ORDERS = {
  'A': {
    "desc": "$[1]$offensive formation$[7]$",
    "status": "form_offensive",
    "adj": "offensive",
    "color": "$[1]$",
    "physical_offense": 1.0,
    "physical_defense": 1.0,
    "arrow_offense": 1.0,
    "arrow_defense": 1.0,
    "morale_cost":{'A':0, 'D':1, 'I':1}
  },
  "D": {
    "adj": "defensive",
    "color": "$[4]$",
    "desc":"$[4]$defensive formation$[7]$",
    "status": "form_defensive",
    "physical_offense": 0.8,
    "physical_defense": 1.2,
    "arrow_offense": 0.8,
    "arrow_defense": 1.2,
    "morale_cost":{'A':1, 'D':0, 'I':1}
  },
  "I": {
    "adj": "scattered",
    "color": "$[1,3]$",
    "desc":"$[4]$scattered formation$[7]$",
    "status": "form_scattered",
    "physical_offense": 1.0,
    "physical_defense": 1.0,
    "arrow_offense": 1.0,
    "arrow_defense": 1.0,
    "morale_cost":{'A':1, 'D':0, 'I':1}
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
    "color": "$[1]$",
    "event": "attack_order",
    "noun": "attack",
    "verb": "marches",
    },
  "D": {
    "color": "$[4]$",
    "event": "defense_order",
    "noun": "defense",
    "verb": "fortifies",
  },
  "I": {
    "color": "$[1,3]$",
    "event": "indirect_order",
    "noun": "skullduggery",
    "verb": "scatters",
   }
}

FINAL_ORDER_LIST = ['A', 'D', 'I'] # keeping the possibility that this list is different

def beats(t1, t2):
  return BEATS[t1] == t2

def order_to_event(order_str):
  return FINAL_ORDERS[order_str]["event"]

def formation_info(form, info_key):
  return FORMATION_ORDERS[form][info_key]

def order_info(order, info_key):
  return FINAL_ORDERS[order][info_key]

def orders_to_winning_army(orders):
  """
  Given a tuple (x,y) of orders, returns the Yomi status, which means a winner (0 or 1) if either
  won, or -1 otherwise.
  """
  x,y = orders
  if x == y:
    return -1
  if BEATS[x] == y:
    return 0
  else:
    return 1
