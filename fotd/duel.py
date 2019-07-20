import random

DUEL_MAX_HEALTH = 20

def _winning_chance_estimate(context, source, target):
  s_str = source.character.power * source.character.power
  t_str = target.character.power * target.character.power
  s_str *= random.uniform(1.0, 1.2) # ego boost
  return s_str/(t_str + s_str)

def duel_commit_old(context, source, target):
  """ 
  gives 2 commitment values for if the source would want to duel target
  """
  actors = [source, target]
  acceptance = None
  dueldata = None
  winning_chance_estimate = _winning_chance_estimate(context, source, target)
  desperation_multiplier = 1.0
  if source.army.morale <= 2 or source.size <= 5:
    desperation_multiplier *= 1.5
  gains_estimate = (5 + target.size)*desperation_multiplier
  losses_estimate = (5 + source.size)
  evwin = winning_chance_estimate*gains_estimate
  evloss = (1-winning_chance_estimate)*losses_estimate
  ratio = evwin/(evwin + evloss)
  acceptance = bool(random.random() < ratio)
  dueldata = (winning_chance_estimate, gains_estimate, losses_estimate, ratio)
  return acceptance, dueldata

def duel_commit(context, source, target):
  """ 
  gives 2 commitment values for if the source would want to duel target
  """
  actors = [source, target]
  errors = [5,0]  # arrogance
  acceptance = False
  dueldata = None
  winning_chance_estimate = _winning_chance_estimate(context, source, target)
  desperation_multiplier = 1.0
  if source.army.morale <= 2 or source.size <= 5:
    errors[0] += 5  # desperation
  if target.is_commander():
    gains_estimate = sum([u.size for u in target.army.present_units()])
  else:
    gains_estimate = target.size
  if source.is_commander():
    losses_estimate = sum([u.size for u in source.army.present_units()])
  else:
    losses_estimate = source.size
  total_gains = 0
  for i in range(2):
    imaginary_duel = Duel(context, None, None, actors, errors)
    healths = imaginary_duel.resolve()
    if healths[1] <= 0:  # won in your mind
      total_gains += gains_estimate
    else:
      total_gains -= losses_estimate

  if total_gains >= 0:
    acceptance = True
  dueldata = (gains_estimate, losses_estimate, total_gains)
  return acceptance, dueldata

# DUEL_SPEECHES = {
#   "challenge": [
#     "Is there no one to fight {csource}?",
#     "Come {ctarget}, it is a good day for a fight.",
#     "You are no match for me, {ctarget}.",
#     "Let's dance, {ctarget}.",
#   ],
#   "accept": [
#     "Ahaha, you asked for it!",
#     "I can beat you with my left hand, {csource}.",
#     "I am surprised you dare to challenge me...",
#     "{csource}! Exactly who I am waiting for!",
#     "You know nothing, {csource}.",
#   ],
#   "deny": [
#     "A good general does not rely on physical strength alone.",
#     "Maybe another day, {csource}.",
#     "Don't bring playground antics to the battlefield.",
#   ],
#   "defeats": [
#     "I bested {ctarget}.",
#     "I have ninety-nine problems and {ctarget} was not one of them.",
#     "Enemy down.",
#     "{ctarget}'s soldiers will now tremble at {csource}'s name.",
#     "Whew. That was a good warmup.",
#     "That was a close one.",
#   ]
# }
# #
# def get_duel_speech(speechtype):
#   return random.choice(DUEL_SPEECHES[speechtype])

class Duel():

  def __init__(self, context, bv, narrator, duelists, errors=(0,0)):
    self.context = context
    self.bv = bv
    self.duelists = duelists
    self.errors = errors # error in power calculation from ego, etc.

  def resolve(self):
    healths = [20, 20]
    health_history = [(20, 20)]
    loser_history = [None]
    damage_history = []
    while (healths[0] > 0 and healths[1] > 0):
      powers = [self.duelists[i].character.power + self.errors[i] for i in [0,1]]
      first_win = random.random() < powers[0]/(powers[0] + powers[1])
      if first_win:
        loser = 1
      else:
        loser = 0
      loser_history.append(loser)
      damage = random.randint(1, 3)
      healths[loser] -= damage
      damage_history.append(damage)
      health_history.append(tuple(healths))
    if self.bv:
      # could be None, for thinking mode
      self.bv.disp_duel(self.duelists[0], self.duelists[1], loser_history, health_history, damage_history)
    return healths
