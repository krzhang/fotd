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
    "viz": "$[3$]raining$[7$]Raining"
  }
}

class Weather(object):
  def __init__(self, text):
    self.text = text

  def __str__(self):
    return WEATHER[self.text]["viz"]

