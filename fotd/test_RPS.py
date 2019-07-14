import game

import pytest

def test_game():
  assert game.test(first_intelligence="INT_AI_NORMAL", second_intelligence ="INT_AI_NORMAL") == 0
