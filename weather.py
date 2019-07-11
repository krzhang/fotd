import random

WEATHER = {
  "sunny": {
    "transitions": {
    },
    "viz": "$[2$]sunny$[7$]"
  },
  "hot": {
    "viz": "$[1$]HOT$[7$]"    
  },
  "raining": {
    "blocks": [],
    "viz": "$[4$]raining$[7$]"
  }
}

class Weather(object):
  def __init__(self, text):
    self.text = text

  def __str__(self):
    return WEATHER[self.text]["viz"]

def random_weather():
  return Weather(random.choice(list(WEATHER)))
