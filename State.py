#! /usr/bin/env python
from copy import deepcopy

class State:

    def __init__(self, turn, dice_roll, position, cash_holdings, bank_money, property_status):
        self.turn = turn
        self.dice_roll = dice_roll
        self.position = position
        self.cash_holdings = cash_holdings
        self.bank_money = bank_money
        self.property_status = property_status

    def __deepcopy__(self, memo):
        # Referred: https://stackoverflow.com/questions/4794244/how-can-i-create-a-copy-of-an-object-in-python

        id_self = id(self)
        _copy = memo.get(id_self)
        if _copy is None:
            _copy = type(self)(
                deepcopy(self.turn, memo),
                deepcopy(self.dice_roll, memo),
                deepcopy(self.position, memo),
                deepcopy(self.cash_holdings, memo),
                deepcopy(self.bank_money, memo),
                deepcopy(self.property_status, memo))
            memo[id_self] = _copy 
        return _copy