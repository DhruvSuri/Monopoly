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
            # self.getSellOrder(state)
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

    ####
    def smooth(self, reward, factor):
        return (reward / factor) / (1 + abs(reward / factor))

    def calculateReward(self, state):
        reward = 0

        playerSign = 1
        key = self.FIRST_PROP_RATIO

        currentPlayerId = state[self.PLAYER_TURN_INDEX] % 2

        if currentPlayerId == 1:  # player id
            playerSign = -1
            key = self.SECOND_PROP_RATIO

        for property in state[self.PROPERTY_STATUS_INDEX]:
            if playerSign * property > 0:  # property owned by the player
                if abs(property) != 7:  # not mortgaged
                    reward += abs(property)
            else:  # property owned by opponent (or not owned by anyone, then no effect on reward)
                if abs(property) != 7:
                    reward -= abs(property)

        transformed_state = self.transform_state(state)
        for item in transformed_state[key]:
            if item >= 0.9:  # item == 1
                reward += 1
            elif item <= 0.1:  # item == 0
                reward -= 1

        alivePlayers = 2.0

        assetFactor = state[self.PLAYER_CASH_INDEX][currentPlayerId]
        totalAsset = state[self.PLAYER_CASH_INDEX][0] + state[self.PLAYER_CASH_INDEX][1]

        assetFactor /= totalAsset
        reward = self.smooth(reward, alivePlayers * 5)  # aliveplayers * 5
        reward = reward + (1 / alivePlayers) * assetFactor

        # print ('player: ' + str(currentPlayerId) + ', reward: ' + str(reward))
        return reward

    def getQVal(self, input_state):
        # getfromdict or getfromNN
        return self.network.run(input_state)

    def createInput(self, tstate, action=0):
        input_state = [0] * self.INPUT_NODES
        input_state[0] = (action + 2.0) / 3.0  # normalizing action between 0 and 1

        j = 1
        for i in range(len(tstate[self.FIRST_PROP_RATIO])):
            input_state[j] = tstate[self.FIRST_PROP_RATIO][i]
            j += 1
            input_state[j] = tstate[self.SECOND_PROP_RATIO][i]
            j += 1

        input_state[j] = tstate[self.PROP_RATIO]
        j += 1
        input_state[j] = tstate[self.MONEY_RATIO]
        j += 1
        input_state[j] = tstate[self.POSITION]

        input_state = self.network.getTensor(input_state)

        return input_state

    # returns vals from QTable ( can be dict, can be NN )
    def calculateQValues(self, state):  # transformed_state
        tstate = self.transform_state(state)
        input_state = self.createInput(tstate)
        tempQ = [0] * self.ACTION_TYPES
        for i in range(self.ACTION_TYPES):
            input_state[0] = (i + 1.0) / 3.0  # normalising the action part
            tempQ[i] = self.getQVal(input_state)
        return tempQ

    def findMaxValues(self, QValues):
        maxQ = QValues[0]
        selectedAction = self.ACTIONS[0]

        for i in range(self.ACTION_TYPES):
            if QValues[i] > maxQ:
                maxQ = QValues[i]
                selectedAction = i - 1
            elif QValues[i] == maxQ:
                rnd1 = random.randint(0, 1000)
                rnd2 = random.randint(0, 1000)
                if rnd2 > rnd1:
                    maxQ = QValues[i]
                    selectedAction = i - 1

        return selectedAction

    def e_greedySelection(self, QValues):
        action = self.ACTION_NOTHING
        rand = random.uniform(0, 1)

        if (rand >= self.network.epsilon):
            action = self.findMaxValues(QValues)
        else:
            action = self.randomAction()

        return action

    def QLearning(self, lastState, lastAction, newState, bestAction, reward):
        lastStateInput = self.createInput(self.transform_state(lastState), lastAction)
        newStateInput = self.createInput(self.transform_state(newState), bestAction)

        QValue = self.network.run(lastStateInput)

        previousQ = QValue
        newQ = self.network.run(newStateInput)

        QValue += self.network.alpha * (reward + self.network.gamma * newQ - previousQ)
        return QValue

    def initParams(self):
        pass

    def agent_start(self, state):
        self.network.currentEpoch += 1
        self.initParams()

        QValues = self.calculateQValues(state)
        action = self.e_greedySelection(QValues)

        self.lastAction = action
        self.lastState = state

        return action

    # returns action
    def agent_step(self, state):

        tempTState = self.transform_state(state)
        if tempTState[self.POSITION] == None:
            return self.ACTION_NOTHING

        if self.lastState is None:
            return self.agent_start(state)

        # state = self.transform_state(state)

        # get reward on state
        reward = self.calculateReward(state)  # original state reqd

        transformed_state = self.transform_state(state)  # needed here ?
        input_state = self.createInput(transformed_state)  # needed here ?

        # Calculate Qvalues
        QValues = self.calculateQValues(state)  # transformed->input state reqd

        # Select action
        action = self.e_greedySelection(QValues)

        QValue = 0
        # tranformed->input state reqd
        QValue = self.QLearning(self.lastState, self.lastAction, state, self.findMaxValues(QValues), reward)
        # QValue = Qlearning(lastState, new Monopoly.RLClasses.Action(lastAction), observation, new Monopoly.RLClasses.Action(findMaxValues(QValues)), reward);

        # trainNeural(createInput(lastState, lastAction), QValue);
        transformed_lastState = self.transform_state(self.lastState)
        input_lastState = self.createInput(transformed_lastState, self.lastAction)
        self.network.train(input_lastState, QValue)

        self.lastAction = action
        self.lastState = state

        return action

    ####

    def parsePhase(self, state):
        '''
        phaseNumber = state["phase"]
        phasePayload = state["phase_payload"]

        # how to distinguish between dice roll bmst and bmst before
        if phaseNumber == 0:
            handleBMSTDecison(state)

        if phaseNumber == 3:
            diceValue = phasePayload["dice_roll"]
            currentPosition = state["player_position"][id]
            # is mod 40 correct?
            newPosition = (currentPosition + diceValue) % 40
            propertyStatus = state["property_status"][newPosition]

            # retrieve the property
            handleBMSTDecison(state)
        '''

    def jailDecision(self, state):
        current_player = state[self.PLAYER_TURN_INDEX] % 2
        playerCash = state[self.PLAYER_CASH_INDEX][current_player]

        if playerCash >= 50:
            return ("P")
        else:
            return ("R")

    def run(self, state):
        return {}

    def getMaxConstructions(self, state):
        monopolyGroups = self.getPropertyGroups()
        currentPlayer = state[self.PLAYER_TURN_INDEX] % 2
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

    def checkSimilarity(self, firstState, secondState, playerId):
        SIMILARITY_THRESHOLD = 0.1
        obs1 = self.transform_state(firstState, playerId)
        obs2 = self.transform_state(secondState, playerId)

        # check Diff in Money
        moneyDif = abs(obs1["propertyRatio"] - obs2["propertyRatio"]) + \
                   abs(obs1["moneyRatio"] - obs2["moneyRatio"])

        if moneyDif >= SIMILARITY_THRESHOLD:
            return False

        # Check diff in position
        if obs1["position"] != obs2["position"]:
            return False

        # check Diff in Group
        obs1Group1 = obs1["firstPropPerc"]
        obs1Group2 = obs1["secPropPerc"]
        obs2Group1 = obs2["firstPropPerc"]
        obs2Group2 = obs2["secPropPerc"]

        diff1 = 0
        diff2 = 0
        for i in range(0, len(obs1Group1)):
            diff1 += abs(obs1Group1[i] - obs2Group1[i])
            diff2 += abs(obs1Group2[i] - obs2Group2[i])
            if diff1 > SIMILARITY_THRESHOLD or diff2 > SIMILARITY_THRESHOLD:
                return False

        return True

    def transform_state(self, state, playerId=None):

        if playerId is None:
            playerId = state[self.PLAYER_TURN_INDEX] % 2

        firstPropertyPercentage, secondPropertyPercentage = self.calculatePropertyGroupPercentage(state)
        moneyRatio, propertyRatio = self.calculateFinancePercentage(state, playerId)
        position = self.getNormalizedPosition(state, playerId)

        # Temp code... Will be removed
        dict = {}
        dict["firstPropPerc"] = firstPropertyPercentage
        dict["secPropPerc"] = secondPropertyPercentage
        dict["moneyRatio"] = moneyRatio
        dict["propertyRatio"] = propertyRatio
        dict["position"] = position
        # print(dict)
        return dict

    def getNormalizedPosition(self, state, playerId):
        properyGroup = self.getPropertyGroups()
        propertyGroupToUnifMapping = {}
        start = 0.1

        orderedPropertyGroups = collections.OrderedDict(sorted(properyGroup.items()))
        for monopolyName, monopolyProperties in orderedPropertyGroups.items():
            for propertyid in monopolyProperties:
                propertyGroupToUnifMapping[propertyid] = round(start, 2)
            start += 0.1

        position = state[self.PLAYER_POSITION_INDEX][playerId]
        return propertyGroupToUnifMapping.get(position, None)

    def calculateFinancePercentage(self, state, playerId):
        return self.calculateMoneyPercentage(state, playerId), self.calculatePropertiesPercentage(state, playerId)

    def calculateMoneyPercentage(self, state, playerId):
        # Assumption: Both player money != 0
        moneyOwned = state[self.PLAYER_CASH_INDEX][playerId]
        opponentId = (playerId + 1) % 2
        opponentMoney = state[self.PLAYER_CASH_INDEX][opponentId]
        return moneyOwned / (moneyOwned + opponentMoney)

    def calculatePropertiesPercentage(self, state, sign):
        # sign = -1 or 1
        propertyStatus = state[self.PROPERTY_STATUS_INDEX]
        total = 0
        owned = 0
        for status in propertyStatus:
            if status != 0:
                total += 1
                if sign == (status / abs(status)):
                    owned += 1

        if total == 0:
            return 0
        else:
            return owned / total

    def calculatePropertyGroupPercentage(self, state):
        propertyGroups = self.getPropertyGroups()
        propertyStatus = state[self.PROPERTY_STATUS_INDEX]
        propertyZeroPercentage = []
        propertyOnePercentage = []

        orderedPropertyGroups = collections.OrderedDict(sorted(propertyGroups.items()))
        i = 0
        for monopolyName, monopolyProperties in orderedPropertyGroups.items():
            ownZero = 0
            ownOne = 0
            for propertyId in monopolyProperties:
                status = propertyStatus[propertyId]
                if status < 0:
                    ownZero += 1
                elif status > 0:
                    ownOne += 1
            if ownOne + ownZero > 0:
                perc = ownZero / (ownOne + ownZero)
                perc = round(perc, 2)
                propertyZeroPercentage.append(perc)
                perc = ownOne / (ownOne + ownZero)
                perc = round(perc, 2)
                propertyOnePercentage.append(perc)
            else:
                propertyZeroPercentage.append(0)
                propertyOnePercentage.append(0)

            i += 1
        return propertyZeroPercentage, propertyOnePercentage

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
        return propertyGroup