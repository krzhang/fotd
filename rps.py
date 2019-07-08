WIN = 1
LOSE = 0

BEATS = {'A':{'A':0, 'D':-1, 'I':1},
         'D':{'A':1, 'D':0, 'I':-1},
         'I':{'A':-1, 'D':1, 'I':0},}

def beats(t1, t2):
  return BEATS[t1][t2] == 1
