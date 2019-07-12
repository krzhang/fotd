import numpy as np

def normalize(myvector):
  boo = sum(myvector)
  return [s/boo for s in myvector]
