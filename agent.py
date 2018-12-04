import constants
import random
import collections

#Actions:
    # Spend(Buy, Auction, Trade)
    # Sell(Sell, Mortgage)
    # Do nothing

#States
    #10(Property Groups percentage)
    #10(Position on property group)
    #2 Finance


class Agent:
    def __init__(self, id):
        self.id = id
        self.PLAYER_TURN_INDEX = 0
        self.PROPERTY_STATUS_INDEX = 1
        self.PLAYER_POSITION_INDEX = 2
        self.PLAYER_CASH_INDEX = 3
        self.PHASE_NUMBER_INDEX = 4
        self.PHASE_PAYLOAD_INDEX = 5

    def getBSMTDecision(self, state):
        playerId = 0
        self.transform_state(state, playerId)
        return None

    def respondTrade(self, state):
        pass

    def buyProperty(self, state):
        return True

    def auctionProperty(self, state):
        return 0

    def receiveState(self, state):
        pass

    def randomAction():
        random.randint(0, 3)


    def parsePhase(self, state):
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

    def jailDecision(self, state):
        current_player = state[self.PLAYER_TURN_INDEX] % 2
        playerCash = state[self.PLAYER_CASH_INDEX][current_player]

        if playerCash >= 50:
            return ("P")
        else:
            return ("R")

    def run(self, state):
        return {}

    def checkSimilarity(self, firstState, secondState, playerId):
        SIMILARITY_THRESHOLD = 0.1
        obs1 = self.transform_state(firstState, playerId)
        obs2 = self.transform_state(secondState, playerId)

        #check Diff in Money
        moneyDif = abs(obs1["propertyRatio"] - obs2["propertyRatio"]) + \
                   abs(obs1["moneyRatio"] - obs2["moneyRatio"])

        if moneyDif >= SIMILARITY_THRESHOLD:
            return False

        #Check diff in position
        if obs1["position"] != obs2["position"]:
            return False


        #check Diff in Group
        obs1Group = dict["firstPropPerc"]
        obs2Group = dict["secPropPerc"]

        diff = 0
        for i in range[0, len(obs1Group)]:
            diff += abs(obs1Group[i] - obs2Group[i])
            if diff > SIMILARITY_THRESHOLD:
                return False

        return True

    def transform_state(self, state, playerId):
        firstPropertyPercentage, secondPropertyPercentage = self.calculatePropertyGroupPercentage(state)
        moneyRatio, propertyRatio = self.calculateFinancePercentage(state, playerId)
        position = self.getNormalizedPosition(state, playerId)


        #Temp code... Will be removed
        dict = {}
        dict["firstPropPerc"] = firstPropertyPercentage
        dict["secPropPerc"] = secondPropertyPercentage
        dict["moneyRatio"] = moneyRatio
        dict["propertyRatio"] = propertyRatio
        dict["position"] = position
        print(dict)
        return dict

    def getNormalizedPosition(self, state, playerId):
        properyGroup = self.getPropertyGroups()
        propertyGroupToUnifMapping = {}
        start = 0.1

        orderedPropertyGroups = collections.OrderedDict(sorted(properyGroup.items()))
        for monopolyName, monopolyProperties in orderedPropertyGroups.items():
            for propertyid in monopolyProperties:
                propertyGroupToUnifMapping[propertyid] = round(start,2)
            start += 0.1

        position = state[self.PLAYER_POSITION_INDEX][playerId]
        return propertyGroupToUnifMapping.get(position, None)

    def calculateFinancePercentage(self, state, playerId):
        return self.calculateMoneyPercentage(state, playerId), self.calculatePropertiesPercentage(state, playerId)

    def calculateMoneyPercentage(self, state, playerId):
        # Assumption: Both player money != 0
        moneyOwned = state[self.PLAYER_CASH_INDEX][playerId]
        opponentId = (playerId+1)%2
        opponentMoney = state[self.PLAYER_CASH_INDEX][opponentId]
        return moneyOwned/(moneyOwned + opponentMoney)

    def calculatePropertiesPercentage(self, state, sign):
        #sign = -1 or 1
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
            return owned/total


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
                    ownZero +=1
                elif status>0:
                    ownOne +=1
            if ownOne+ownZero > 0:
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
            group = propertyGroup.get(value["monopoly"],None)
            if group == None and value.get("monopoly_group_elements", None) != None:
                group = set(value.get("monopoly_group_elements", None))
                group.add(id)
            propertyGroup[value["monopoly"]] = group
        propertyGroup.pop('None', None)
        return propertyGroup