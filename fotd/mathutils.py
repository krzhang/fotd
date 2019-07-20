import numpy as np

def normalize(myvector):
  newvector = myvector.copy()
  # for i, v in enumerate(newvector):
  #   if v > 1: # inf
  #     newvector[i] = 1
  #   if v < 0: # -info
  #     newvector[i] = 0
  #   if np.isnan(v):
  #     newvector[i] = 0
  boo = sum(newvector)
  return [s/boo for s in newvector]
