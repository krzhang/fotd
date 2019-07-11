WIN = 1
LOSE = 0

BEATS = {'A':{'A':0, 'D':-1, 'I':1},
         'D':{'A':1, 'D':0, 'I':-1},
         'I':{'A':-1, 'D':1, 'I':0},}

FORMATION_ORDERS = {
  'O': {
    "desc": "$[1$]offensive formation$[7$]",
    "status": "form_offensive",
    "adj": "offensive",
    "short": "$[1$]O$[7$]"
  },
  "D": {
    "adj": "defensive",
    "desc":"$[4$]Defensive Formation$[7$]",
    "status": "form_defensive",
    "short": "$[4$]D$[7$]"
  }
}

STRATEGIC_ORDERS = {
  "A": {
    "event": "attack_order",
    "short": "$[1$]A$[7$]"
    },
  "D": {
    "event": "defense_order",
    "short": "$[4$]D$[7$]"
  },
  "I": {
    "event": "indirect_order",
    "short": "$[1,3$]I$[7$]"
  }
}
o2e = {"A": "attack_order", "D": "defense_order", "I":"indirect_order"}

def beats(t1, t2):
  return BEATS[t1][t2] == 1

def order_to_event(order_str):
  return STRATEGIC_ORDERS[order_str]["event"]
