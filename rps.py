WIN = 1
LOSE = 0

BEATS = {'A':{'A':0, 'D':-1, 'I':1},
         'D':{'A':1, 'D':0, 'I':-1},
         'I':{'A':-1, 'D':1, 'I':0},}

FORMATION_ORDERS = {
  'O': {
    "desc": "Offensive Formation",
    "status": "form_offensive",
    "adj": "offensive",
  },
  "D": {
    "adj": "defensive",
    "desc":"Defensive Formation",
    "status": "form_defensive"
  }
}

STRATEGIC_ORDERS = {
  "A": {
    "event": "attack_order",
    },
  "D": {
    "event": "defense_order",
  },
  "I": {
    "event": "indirect_order"
  }
}
o2e = {"A": "attack_order", "D": "defense_order", "I":"indirect_order"}

def beats(t1, t2):
  return BEATS[t1][t2] == 1

def order_to_event(order_str):
  return STRATEGIC_ORDERS[order_str]["event"]
