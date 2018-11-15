#! /usr/bin/env python

from Game import Game

class TestAgent:
	def __init__(self, id):
		self.id = id

	def getBMSTDecision(self, state):
		return None

	def respondTrade(self, state):
		return None
	
	def buyProperty(self, state):
		return True
	
	def auctionProperty(self, state):
		return False
	
	def receiveState(self, state):
		self.state = state
		
	def respondMortgage(self, state):
		return True

	def jailDecision(self, state):
		return ("P")

def testJailOnDoubles(adjudicator):
    diceRolls = [[(1,4)], [(5, 5), (4, 4), (3, 3)]]

    _, currState = adjudicator.run([TestAgent(1), TestAgent(2)], diceRolls)

    return currState.position == (5, -1)

def testJailOnGoToJailCell(adjudicator):
    diceRolls = [[(1,4)], [(2, 5)], [(5, 5), (6, 6), (1, 2)]]
    
    _, currState = adjudicator.run([TestAgent(1), TestAgent(2)], diceRolls)

    return currState.position == (-1, 7)

def testGetOutOfJailUsingDoubles(adjudicator):
    diceRolls = [[(5, 5), (4, 4), (3, 3)], [(1, 4)], [(2, 2)]]
    
    _, currState = adjudicator.run([TestAgent(1), TestAgent(2)], diceRolls)

    return currState.position == (4, 5)

def testPayTaxes(adjudicator):
    diceRolls = [[(1, 3)]]
    
    _, currState = adjudicator.run([TestAgent(1), TestAgent(2)], diceRolls)

    return currState.position == (4, 0) \
        and currState.cashHoldings == (1300, 1500)

def testPayRentIfNotOwned(adjudicator):
    diceRolls = [[(1, 2)], [(2, 1)]]
    
    _, currState = adjudicator.run([TestAgent(1), TestAgent(2)], diceRolls)

    return currState.position == (3, 3) \
        and currState.cashHoldings == (1444, 1496) \
        and currState.propertyStatus[3] == 1

tests = [
    testJailOnDoubles,
    testJailOnGoToJailCell,
    testGetOutOfJailUsingDoubles,
    # testGetOutOfJailUsingChanceCard
    # testGetOutOfJailUsingCommunityCard
    # testHouseGettingBuilt
    # testBuyPropertyIfEmpty
    testPayRentIfNotOwned,
    testPayTaxes
]

def runTests():
    failedTests = []
    for test in tests:
        adjudicator = Game()
        result = test(adjudicator)
        if not result:
            failedTests.append(test.__name__)
    if len(failedTests) == 0: 
        print("All tests passed!")
    else:
        print("Following tests failed" + str(failedTests))

runTests()