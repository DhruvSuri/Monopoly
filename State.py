#! /usr/bin/env python
from copy import deepcopy
import Constant as constant
from logger import logger

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

    def allPropertiesOfMonopolyOwned(self, playerId, position, monopolyGroup):
        propertyOwner = self.getPropertyOwner(position)

        for position in monopolyGroup:
            if propertyOwner != self.getPropertyOwner(position):
                return False

        return True

    def allHousesEvenlyDistributed(self, playerId, position, monopolyGroup):
        max = 0
        min = 10 
        #Property between -7 and 7
        monopolyGroup.append(position)
        for position in monopolyGroup:
            status = abs(self.propertyStatus[position])
            if status == 0:
                return False
            if status < min:
                min = status
            if status > max:
                max = status
        #Diff of <=1 in min and max houses and property status = min
        return (max-min <=1) and (abs(self.propertyStatus[position]) == min)

    def updateHouseStatus(self, playerId, position):
        #All conditions for buying house must satisfy!!
        status = self.propertyStatus[position]
        if status < 0:
            self.propertyStatus[position] = status-1
        else:
            self.propertyStatus[position] = status+1

    def allHouseConditionsSatisfied(self, playerId, position, monopolyGroup):
        if (self.allHousesEvenlyDistributed(playerId, position, monopolyGroup) \
            and self.allPropertiesOfMonopolyOwned(playerId, position, monopolyGroup) \
            and self.propertyStatus[position] > -5 and self.propertyStatus[position] < 5):
            #Houses can be built from -5 to 5
            return True
        
        return False

    def getPropertyOwner(self, position):
        # Player 1
        if self.propertyStatus[position] > 0:
            return 0
        # Player 2
        elif self.propertyStatus[position] < 0:
            return 1
        else:
            return -1

    def getPropertyStatus(self, position):
        return self.propertyStatus[position]

    def updatePropertyStatus(self, position, playerId):
        sign = 1
        if playerId == 1:
            sign = -1
        return sign

    def updateCashHolding(self, playerId, cashToAdd):
        newCashHolding = list(self.cashHoldings)
        newCashHolding[playerId] = self.cashHoldings[playerId] + cashToAdd
        self.cashHoldings = tuple(newCashHolding)