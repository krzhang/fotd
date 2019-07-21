import game

import pytest

def test_game():
  assert len(game.test(first_intelligence="AI_HEU_HEU",
                       second_intelligence ="AI_HEU_HEU")) == 2
