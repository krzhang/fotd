WIN = 1
LOSE = 0

BEATS = {'A':'I',
         'D':'A',
         'I':'D'}


FORMATIONS = {
  'O': {
    "desc": "$[1]$offensive formation$[7]$",
    "status": "form_offensive",
    "adj": "offensive",
    "color": "$[1]$",
    "short": "$[1]$O$[7]$",
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
    "short": "$[4]$D$[7]$",
    "physical_offense": 0.8,
    "physical_defense": 1.2,
    "arrow_offense": 0.8,
    "arrow_defense": 1.2,
    "morale_cost":{'A':1, 'D':0, 'I':1}
  }
}

STRATEGIC_ORDERS = {
  "A": {
    "color": "$[1]$",
    "event": "attack_order",
    "short": "$[1]$A$[7]$",
    "noun": "attack",
    "verb": "marches",
    },
  "D": {
    "color": "$[4]$",
    "event": "defense_order",
    "short": "$[4]$D$[7]$",
    "noun": "defense",
    "verb": "fortifies",
  },
  "I": {
    "color": "$[1,3]$",
    "event": "indirect_order",
    "short": "$[1,3]$I$[7]$",
    "noun": "skullduggery",
    "verb": "scatters",
   }
}
# o2e = {"A": "attack_order", "D": "defense_order", "I":"indirect_order"}

def beats(t1, t2):
  return BEATS[t1] == t2

def order_to_event(order_str):
  return STRATEGIC_ORDERS[order_str]["event"]

def formation_info(form, info_key):
  return FORMATIONS[form][info_key]

def order_info(order, info_key):
  return STRATEGIC_ORDERS[order][info_key]

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