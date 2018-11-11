#! /usr/bin/env python
from copy import deepcopy

class State:

    def __init__(self, turn, dice_roll, position):
        self.turn = turn
        self.dice_roll = dice_roll
        self.position = position

    def __deepcopy__(self, memo):
        # Referred: https://stackoverflow.com/questions/4794244/how-can-i-create-a-copy-of-an-object-in-python

        id_self = id(self)
        _copy = memo.get(id_self)
        if _copy is None:
            _copy = type(self)(
                deepcopy(self.turn, memo),
                deepcopy(self.dice_roll, memo),
                deepcopy(self.position, memo))
            memo[id_self] = _copy 
        return _copy