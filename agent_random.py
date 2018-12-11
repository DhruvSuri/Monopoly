import constants
import random
import collections
from network import Network


# Actions:
# Spend(Buy, Auction, Trade)
# Sell(Sell, Mortgage)
# Do nothing

# States
# 10(Property Groups percentage)
# 10(Position on property group)
# 2 Finance


class RandomAgent:
    def __init__(self, id):
        self.id = id
        self.PLAYER_TURN_INDEX = 0
        self.PROPERTY_STATUS_INDEX = 1
        self.PLAYER_POSITION_INDEX = 2
        self.PLAYER_CASH_INDEX = 3
        self.PHASE_NUMBER_INDEX = 4
        self.PHASE_PAYLOAD_INDEX = 5
        self.ACTION_TYPES = 3
        self.ACTIONS = [-1, 0, 1]  # -1 -> earn money by selling, 0->do nothing, 1->build, buy type action
        self.ACTION_SELL = -1
        self.ACTION_NOTHING = 0
        self.ACTION_BUY = 1
        self.QTable = {}
        self.FIRST_PROP_RATIO = 'firstPropPerc'
        self.SECOND_PROP_RATIO = 'secPropPerc'
        self.MONEY_RATIO = 'moneyRatio'
        self.PROP_RATIO = 'propertyRatio'
        self.POSITION = 'position'
        self.lastState = None
        self.lastAction = None
        self.INPUT_NODES = 24
        self.network = Network()
        self.constructionException = ["Railroad", "Utility"]

    def getBSMTDecision(self, state):
        action = self.randomAction()
        # action = 1
        if action == 1:
            constructions = self.getMaxConstructions(state)
            if constructions != None:
                return ["B", constructions]
            else:
                return None

        elif action == -1:
            pass
        else:
            return None

    def respondTrade(self, state):
        pass

    def buyProperty(self, state):
        action = self.randomAction()
        # action = self.agent_step(state)
        if action == 1:
            return True
        else:
            return False

    def auctionProperty(self, state):
        return 0

    def receiveState(self, state):
        pass

    def randomAction(self):
        return random.choice(self.ACTIONS)

    def jailDecision(self, state):
        current_player = state[self.PLAYER_TURN_INDEX] % 2
        playerCash = state[self.PLAYER_CASH_INDEX][current_player]

        if playerCash >= 50:
            return ("P")
        else:
            return ("R")

    def getMaxConstructions(self, state):
        monopolyGroups = self.getPropertyGroups()
        currentPlayer = self.id - 1
        playerCash = state[self.PLAYER_CASH_INDEX][currentPlayer]
        propertyStatus = state[self.PROPERTY_STATUS_INDEX]
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
                    if propertiesConstructionOrder.get(propertyId, None) == None:
                        propertiesConstructionOrder[propertyId] = 1
                    else:
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
        propertyStatus = state[self.PROPERTY_STATUS_INDEX]
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