#! /usr/bin/env python
from copy import deepcopy
import Constant as constant

class State:

    def __init__(self, turn, diceRoll, position, cashHoldings, bankMoney, propertyStatus):
        self.turn = turn
        self.diceRoll = diceRoll
        self.position = position
        self.cashHoldings = cashHoldings
        self.bankMoney = bankMoney
        self.propertyStatus = propertyStatus

    def __deepcopy__(self, memo):
        # Referred: https://stackoverflow.com/questions/4794244/how-can-i-create-a-copy-of-an-object-in-python

        id_self = id(self)
        _copy = memo.get(id_self)
        if _copy is None:
            _copy = type(self)(
                deepcopy(self.turn, memo),
                deepcopy(self.diceRoll, memo),
                deepcopy(self.position, memo),
                deepcopy(self.cashHoldings, memo),
                deepcopy(self.bankMoney, memo),
                deepcopy(self.propertyStatus, memo))
            memo[id_self] = _copy 
        return _copy
    
    def isPlayerInJail(self, playerId):
        return self.position[playerId] == constant.IN_JAIL_INDEX

    def getPlayerPosition(self, playerId):
        return self.position[playerId]

    def isPropertyEmpty(self, position):
        return self.propertyStatus[position] == constant.INITIAL_PROPERTY_STATUS

    def getPropertyOwner(self, position):
        # Player 1
        if self.propertyStatus[position] > 0:
            return 0
        # Player 2
        else:
            return 1

    def getPropertyStatus(self, position):
        return self.propertyStatus[position]

    def updatePropertyStatus(self, position, playerId):
        sign = 1
        if playerId == 1:
            sign = -1
        
        self.propertyStatus[position] = sign

    def updateCashHolding(self, playerId, cashToAdd):
        newCashHolding = list(self.cashHoldings)
        newCashHolding[playerId] = self.cashHoldings[playerId] + cashToAdd
        self.cashHoldings = tuple(newCashHolding)