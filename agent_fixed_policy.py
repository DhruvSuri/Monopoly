import random
import numpy as np
import constants

'''
Tunable Parameters
'''
TURNS_JAIL_HEURISTICS = 30
BUYING_PROPERTY_PROBABILITY = 0.8
BUILD_HOTEL_PROBABILITY = 0.8
AUCTION_BID_MIN = 0.4
AUCTION_BID_MAX = 0.7

'''
State Index
'''
PLAYER_TURN_INDEX = 0
PROPERTY_STATUS_INDEX = 1
PLAYER_POSITION_INDEX = 2
PLAYER_CASH_INDEX = 3
PHASE_NUMBER_INDEX = 4
PHASE_PAYLOAD_INDEX = 5
DEBT_INDEX = 6
STATE_HISTORY_INDEX = 7

'''
Property Index
'''
CHANCE_GET_OUT_OF_JAIL_FREE = 40
COMMUNITY_GET_OUT_OF_JAIL_FREE = 41

class Agent:

    def __init__(self, id):
        self.id = id
        self.stateHist = []

        self.jailDiceRolls = 0

        self.constructionException = ["Railroad", "Utility"]

    def getBSMTDecision(self, state):
        # Check for Debt field and clear
        debt = self.getDebt(state)
        if debt > 0:
            cash = self.getCash(state)

            # Sell/Mortgage cheapest property
            if cash < debt:
                # Try selling first
                action = self.sell(state)

                # If nothing to sell then mortgage
                if action == None :
                    action = self.mortgage(state)
                
                return action
            # Enough cash to handle debt. Do Nothing
        
        return self.getMaxConstructions(state)
        
    def respondTrade(self, state):
        return None

    def buyProperty(self, state):
        if np.random.uniform(0,1) <= BUYING_PROPERTY_PROBABILITY:
            return True
        return False

    def auctionProperty(self, state):
        position = self.getTurnPlayerPosition(state)
        price = self.getPropertyPrice(position)

        return np.random.uniform(AUCTION_BID_MIN, AUCTION_BID_MAX) * price

    def jailDecision(self, state):
        turns = state[PLAYER_TURN_INDEX]
        self.jailDiceRolls += 1

        if turns <= TURNS_JAIL_HEURISTICS:
            self.jailDiceRolls = 0

            if self.hasJailCard(state):
                return ("C", self.getJailCard(state))
            return "P"
        
        # Try Stalling and evade paying rent. Can't evade third time
        if self.jailDiceRolls == 3:
            self.jailDiceRolls = 0

            if self.hasJailCard(state):
                return ("C", self.getJailCard(state))

            return "P"

        return "R"

    def receiveState(self, state):
        self.stateHist.append(state)

    def getTurns(self):
        return len(self.stateHist)

    def hasJailCard(self, state):
        return self.isPropertyOwned(state[PROPERTY_STATUS_INDEX][CHANCE_GET_OUT_OF_JAIL_FREE]) \
            or self.isPropertyOwned(state[PROPERTY_STATUS_INDEX][COMMUNITY_GET_OUT_OF_JAIL_FREE])

    def getJailCard(self, state):
        if self.isPropertyOwned(state[PROPERTY_STATUS_INDEX][CHANCE_GET_OUT_OF_JAIL_FREE]):
            return CHANCE_GET_OUT_OF_JAIL_FREE
        elif self.isPropertyOwned(state[PROPERTY_STATUS_INDEX][COMMUNITY_GET_OUT_OF_JAIL_FREE]):
            return COMMUNITY_GET_OUT_OF_JAIL_FREE

        raise Exception('No jail card found')

    def getPlayerTurn(self, state):
        return state[PLAYER_TURN_INDEX]%2

    def getTurnPlayerPosition(self, state):
        playerTurn = self.getPlayerTurn(state)
        return state[PLAYER_POSITION_INDEX][playerTurn]

    def getPropertyPrice(self, position):
        return constants.board[position]['price']

    def getDebt(self, state):
        return state[DEBT_INDEX][(self.id - 1) * 2 + 1]

    def getCash(self, state):
        return state[PLAYER_CASH_INDEX][self.id - 1]

    def sell(self, state):
        ownedProperties = self.getOwnedProperties(state)

        sellingProperty = None
        for tup in ownedProperties:
            if tup[1] > 1:
                sellingProperty = (tup[0], 1)
                break

        if sellingProperty != None:
            return ('S', [sellingProperty])

        return None

    def mortgage(self, state):
        ownedProperties = self.getOwnedProperties(state)

        mortgagingProperty = None
        for tup in ownedProperties:
            if tup[1] == 1:
                mortgagingProperty = tup[0]
                break

        if mortgagingProperty != None:
            return ('M', [mortgagingProperty])

        return None

    def getOwnedProperties(self, state):
        properties = []
        for i, val in enumerate(state[PROPERTY_STATUS_INDEX]):
            if self.isPropertyOwned(val) \
                and i != 0 \
                and i != CHANCE_GET_OUT_OF_JAIL_FREE \
                and i != COMMUNITY_GET_OUT_OF_JAIL_FREE:
                properties.append((i, abs(val), self.getPropertyPrice(i)))
        
        properties.sort(key=lambda tup: (tup[1], tup[2]), reverse = True)

        return properties

    def isPropertyOwned(self, propertyStatus):
        return (self.id == 1 and propertyStatus > 0) or (self.id == 2 and propertyStatus < 0)



    # RL Agent Copied Code

    def getMaxConstructions(self, state):
        monopolyGroups = self.getPropertyGroups()
        currentPlayer = state[PLAYER_TURN_INDEX] % 2
        playerCash = state[PLAYER_CASH_INDEX][currentPlayer]
        propertyStatus = state[PROPERTY_STATUS_INDEX]
        propertiesConstructionOrder = {}

        for (groupName, groupPositions) in monopolyGroups.items():
            if groupName in self.constructionException:
                continue
            if not self.allPropertiesOfMonopolyOwned(state, currentPlayer, groupPositions):
                continue
            else:
                playerCash = self.buildPropertiesInOrder(playerCash, propertyStatus, groupPositions,
                                                         propertiesConstructionOrder)

        if len(propertiesConstructionOrder) == 0:
            return None
        else:
            constructionOrderResult = []
            for propertyId, constructions in propertiesConstructionOrder.items():
                constructionOrderResult.append((propertyId, constructions))
            return constructionOrderResult

    def buildPropertiesInOrder(self, playerCashHolding, propertyStatus, groupPositions, propertiesConstructionOrder):
        min, max, statusDict = self.getMinMaxPropertyStatus(propertyStatus, groupPositions)

        # Bringing all properties at same level
        if min < max:
            for propertyId, status in statusDict.items():
                if status == min and playerCashHolding > self.getConstructionPrice(propertyId):
                    propertiesConstructionOrder[propertyId] += 1
                    statusDict[propertyId] += 1
                    playerCashHolding -= self.getConstructionPrice(propertyId)
                else:
                    return playerCashHolding

        # Incrementally, Increasing 1 construction on each property
        # Min=Max and Max construction is Hotel(6)
        sortedPropertyTyples = sorted(statusDict.items(), key=lambda x: self.getConstructionPrice(x[0]))
        # statusDict = sorted(statusDict.items(), key =lambda item: item[1])

        for (propertyId, status) in sortedPropertyTyples:
            statusDict[propertyId] = status
            if status < 6 and playerCashHolding > self.getConstructionPrice(propertyId):
                statusDict[propertyId] += 1
                if propertiesConstructionOrder.get(propertyId, None) == None:
                    propertiesConstructionOrder[propertyId] = 1
                else:
                    propertiesConstructionOrder[propertyId] += 1
                playerCashHolding -= self.getConstructionPrice(propertyId)
                max = statusDict[propertyId]
            else:
                break
        return playerCashHolding

    def getConstructionPrice(self, propertyId):
        property = constants.board[propertyId]
        return property["build_cost"]

    def getMinMaxPropertyStatus(self, propertyStatus, groupPositions):
        # Calculate Min and Max constructions on property. # Property between -7 and 7
        min = 10
        max = 0
        dict = {}
        for position in groupPositions:
            status = abs(propertyStatus[position])
            dict[position] = status
            if status < min:
                min = status
            if status > max:
                max = status
        return min, max, dict

    def allPropertiesOfMonopolyOwned(self, state, playerId, monopolyGroup):
        propertyOwner = self.getPropertyOwner(state, monopolyGroup[0])
        if playerId != propertyOwner:
            return False

        for position in monopolyGroup:
            if propertyOwner != self.getPropertyOwner(state, position):
                return False
        return True

    def getPropertyOwner(self, state, position):
        # Player 1
        propertyStatus = state[PROPERTY_STATUS_INDEX]
        if propertyStatus[position] > 0:
            return 0
        # Player 2
        elif propertyStatus[position] < 0:
            return 1
        else:
            return -1

    def getPropertyGroups(self):
        propertyGroup = {}
        for id, value in constants.board.items():
            group = propertyGroup.get(value["monopoly"], None)
            if group == None and value.get("monopoly_group_elements", None) != None:
                group = set(value.get("monopoly_group_elements", None))
                group.add(id)
            propertyGroup[value["monopoly"]] = group
        propertyGroup.pop('None', None)

        for key, value in propertyGroup.items():
            propertyGroup[key] = list(value)

        tupleList = []
        for key in self.constructionException:
            tupleList.append((key, propertyGroup[key]))
            propertyGroup.pop(key)
        sortedPropertyTyples = sorted(propertyGroup.items(), key=lambda x: sum(x[1]) / len(x[1]))
        tupleList.extend(sortedPropertyTyples)
        return dict(tupleList)