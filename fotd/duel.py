import random

DUEL_BASE_CHANCE = 0.25
DUEL_MAX_HEALTH = 20

def _winning_chance_estimate(context, source, target):
  s_str = source.character.power * source.character.power
  t_str = target.character.power * target.character.power
  s_str *= random.uniform(1.0, 1.2) # ego boost
  return s_str/(t_str + s_str)

def duel_commit(context, source, target):
  """ gives 2 commitment values for if the 2 sides would want to duel """
  actors = [source, target]
  acceptances = [None, None]
  dueldata = [None, None]
  if random.random() < DUEL_BASE_CHANCE:
    for i in [0, 1]:
      actor = actors[i]
      opponent = actors[1-i]
      winning_chance_estimate = _winning_chance_estimate(context, actor, opponent)
      desperation_multiplier = 1.0
      if actor.army.morale <= 2 or actor.size <= 5:
        desperation_multiplier *= 1.5
      if i == 1: # on defense; maybe an honor/bravery check later
        pass
      gains_estimate = (5 + opponent.size)*desperation_multiplier
      losses_estimate = (5 + actor.size)
      evwin = winning_chance_estimate*gains_estimate
      evloss = (1-winning_chance_estimate)*losses_estimate
      ratio = evwin/(evwin + evloss)
      acceptances[i] = bool(random.random() < ratio)
      dueldata[i] = (winning_chance_estimate, gains_estimate, losses_estimate, ratio)
  return tuple(acceptances), tuple(dueldata)

DUEL_SPEECHES = {
  "challenge": [
    "Is there no one to fight {csource}?",
    "Come {ctarget}, it is a good day for a fight.",
    "You are no match for me, {ctarget}.",
    "Let's dance, {ctarget}.",
  ],
  "accept": [
    "Ahaha, you asked for it!",
    "I can beat you with my left hand, {csource}.",
    "I am surprised you dare to challenge me...",
    "{csource}! Exactly who I am waiting for!",
    "You know nothing, {csource}.",
  ],
  "deny": [
    "A good general does not rely on physical strength alone.",
    "Maybe another day, {csource}.",
    "Don't bring playground antics to the battlefield.",
  ],
  "defeats": [
    "I bested {ctarget}.",
    "I have a hundred problems and {ctarget} was not one of them.",
    "Whew. That was a good warmup."
  ]
}

def get_pre_duel_speech(speechtype):
  return random.choice(DUEL_SPEECHES[speechtype])
