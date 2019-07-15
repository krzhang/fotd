import csv

##############################################################################
# This file no longer needs to work, as now all the data is in events.csv. However, keeping
# here for reference in case we needt write more loaders / dumpers
###################################################################
  
EVENTS_ORDERS = {
  "order_received": {
  },
  "attack_order": {},
  "defense_order": {},
  "indirect_order": {},
  "panicked_order": {
  },
  "provoked_order": {
  }
}

for ev in EVENTS_ORDERS:
  if "panic_blocked" not in EVENTS_ORDERS[ev]:
    EVENTS_ORDERS[ev]["panic_blocked"] = False
  EVENTS_ORDERS[ev]["actors"] = ["ctarget"]
  EVENTS_ORDERS[ev]["primary_actor"] = "ctarget"
  EVENTS_ORDERS[ev]["event_type"] = "order_phase"
  
EVENTS_GENERIC_CTARGETTED = {
  "arrow_strike": {},
  "duel_consider": {},
  "duel_accepted": {},
  "engage": {},
  "march": {},
  "indirect_raid": {},
  "physical_clash": {},
  "physical_strike": {}
}

for ev in EVENTS_GENERIC_CTARGETTED:
  EVENTS_GENERIC_CTARGETTED[ev]["panic_blocked"] = True
  EVENTS_GENERIC_CTARGETTED[ev]["actors"] = ["csource", "ctarget"]
  EVENTS_GENERIC_CTARGETTED[ev]["primary_actor"] = "csource"
  EVENTS_GENERIC_CTARGETTED[ev]["event_type"] = "source_target"

# eventually maybe separate things out with one ctarget unit
  
EVENTS_MISC = {
  # "army_destroyed": {
  #   "actors":["ctarget_army"],
  #   "primary_actor": "ctarget_army"
  # },
  "make_speech": {
    "actors":["ctarget"],
    "primary_actor": "ctarget"
  },
  "receive_damage": {
    "actors":["ctarget"],
    "primary_actor": "ctarget"
  },
  "receive_status": {
    "actors":["ctarget"],
    "primary_actor": "ctarget"
    #"need_live_actors":False # maybe need "Captured" etc.
  },
  "order_change": {
    "actors":["ctarget_army"],
    "primary_actor": "ctarget_army"
  },
  "change_morale": {
    "actors":["ctarget_army"],
    "primary_actor": "ctarget_army"
  },
  "order_yomi_win": {
    "actors":["ctarget_army"],
    "primary_actor": "ctarget_army"
  },
}

for ev in EVENTS_MISC:
  EVENTS_MISC[ev]["event_type"] = "misc"

EVENTS_PAIRED_TARGETTED = {
  "counter_arrow_strike": {
    "can_aoe": False
    },
  "fire_tactic": {
    "can_aoe": True
    },
  "jeer_tactic": {
    "can_aoe": True
    },
  "lure_tactic": {
    "can_aoe": False
    },
  "panic_tactic": {
    "can_aoe": True
    },
  "flood_tactic": {
    "can_aoe": True
    },
  "_fire_tactic_success": {},
  "_panic_tactic_success": {},
  "_jeer_tactic_success": {},
  "_flood_tactic_success": {},
}

for ev in EVENTS_PAIRED_TARGETTED:
  EVENTS_PAIRED_TARGETTED[ev]["panic_blocked"] = True
  EVENTS_PAIRED_TARGETTED[ev]["actors"] = ["csource", "ctarget"]
  EVENTS_PAIRED_TARGETTED[ev]["primary_actor"] = "csource"
  EVENTS_PAIRED_TARGETTED[ev]["event_type"] = "source_target_skill"
  
  EVENTS_STATUS = {
  "remove_status_probabilistic": {},
  "burned_bot": {},
  "burned_eot": {},
  "_trymode_activation_success": {
  },
  "trymode_status_bot": {
  }
}

for ev in EVENTS_STATUS:
  if "panic_blocked" not in EVENTS_STATUS[ev]:
    EVENTS_STATUS[ev]["panic_blocked"] = False
  EVENTS_STATUS[ev]["actors"] = ["ctarget"]
  EVENTS_STATUS[ev]["primary_actor"] = "ctarget"
  EVENTS_STATUS[ev]["event_type"] = "status"
  
EVENTS = dict(list(EVENTS_ORDERS.items()) +
              list(EVENTS_GENERIC_CTARGETTED.items()) +
              list(EVENTS_MISC.items()) +
              list(EVENTS_PAIRED_TARGETTED.items()) +
              list(EVENTS_STATUS.items()))

for ev in EVENTS:
  if "can_aoe" not in EVENTS[ev]:
    EVENTS[ev]["can_aoe"] = False
  if "panic_blocked" not in EVENTS[ev]:
    EVENTS[ev]["panic_blocked"] = False


my_dict = EVENTS

with open('test.csv', 'w') as f:
  f.write("event_name, event_type, actors, primary_actor, can_aoe, panic_blocked")
  for key in my_dict.keys():
    f.write("%s, %s, %s, %s, %s, %s\n"%(key,
                                        my_dict[key]['event_type'],
                                        my_dict[key]['actors'],
                                        my_dict[key]['primary_actor'],
                                        my_dict[key]['can_aoe'],
                                        my_dict[key]['panic_blocked'], ))
