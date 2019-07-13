import game

import pytest

def test_game():
  assert game.test(first_intelligence="INT_AI_ROCK", second_intelligence ="INT_AI_PAPER") == 0
