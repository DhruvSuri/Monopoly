#! /usr/bin/env python

from Game import Game
from logger import logger

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
		# ToDo: Different actions needs to be modelled R, P or C
		# Currently in greedy approach modelling as P
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

def testHouseGettingBuilt(adjudicator):
	logger.debug('Testing House getting built for Property Marvin Gardens')
	diceRolls = [[(6,6), (6,5), (1,2)], [(1,2)], [(1,2)], [(2,4)], [(6,5)], [(1,3)] ,[(6,6), (6,6), (1,2)], [(1,3)], [(1,1)]]
	_, currState = adjudicator.run([TestAgent(1), TestAgent(2)], diceRolls)
	return currState.propertyStatus[29] == 2

tests = [
    testJailOnDoubles,
    testJailOnGoToJailCell,
    testGetOutOfJailUsingDoubles,
    # testGetOutOfJailUsingChanceCard
    # testGetOutOfJailUsingCommunityCard
    testHouseGettingBuilt
    # testBuyPropertyIfEmpty
    # testPayRentIfNotOwned
    # testPayTaxes
]

def runTests():
    allPassed = True
    for test in tests:
        adjudicator = Game()
        logger.debug('\n\n\nSTARTING NEW TEST CASE: %s\n', test.__name__)
        result = test(adjudicator)
        if not result:
            print(test.__name__ + " failed!")
            allPassed = False
    if allPassed: print("All tests passed!")

runTests()