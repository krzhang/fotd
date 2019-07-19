import game

import pytest

def test_game():
  assert len(game.test(first_intelligence="AI_WIP",
                       second_intelligence ="AI_WIP")) == 2
