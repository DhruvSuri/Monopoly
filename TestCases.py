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
		return ("P")

def testJailOnDoubles(adjudicator):
	logger.debug('Testing Go to jail on 3 doubles')
	diceRolls = [[(1,4)], [(5, 5), (4, 4), (3, 3)]]
	
	_, currState = adjudicator.run([TestAgent(1), TestAgent(2)], diceRolls, None, None, False)

	return currState.position == (5, -1)

def testJailOnGoToJailCell(adjudicator):
	logger.debug('Testing going to jail if landed on GoToJail cell')
	diceRolls = [[(1,4)], [(2, 5)], [(5, 5), (6, 6), (1, 2)]]
	
	_, currState = adjudicator.run([TestAgent(1), TestAgent(2)], diceRolls, None, None, False)

	return currState.position == (-1, 7)

def testGetOutOfJailUsingDoubles(adjudicator):
	logger.debug('Testing Getting out of jail using doubles on dice')
	diceRolls = [[(5, 5), (4, 4), (3, 3)], [(1, 4)], [(2, 2)]]
	
	_, currState = adjudicator.run([TestAgent(1), TestAgent(2)], diceRolls, None, None, False)

	return currState.position == (4, 5)

def testPayTaxes(adjudicator):
	logger.debug('Testing Taxes are paid correctly')
	diceRolls = [[(1, 3)]]
	
	_, currState = adjudicator.run([TestAgent(1), TestAgent(2)], diceRolls, None, None, False)

	return currState.position == (4, 0) \
		and currState.cashHoldings == (1300, 1500)

def testHouseGettingBuilt(adjudicator):
	logger.debug('Testing House getting built for Property Marvin Gardens')
	diceRolls = [[(6,6), (6,5), (1,2)], [(1,2)], [(1,2)], [(2,4)], [(6,5)], [(1,3)] ,[(6,6), (6,6), (1,2)], [(1,3)], [(1,1)]]
	_, currState = adjudicator.run([TestAgent(1), TestAgent(2)], diceRolls, None, None, False)
	return currState.propertyStatus[29] == 2

def testPayRentIfNotOwned(adjudicator):
	logger.debug('Testing Rent is paid correctly if property not owned')
	diceRolls = [[(1, 2)], [(2, 1)]]
	
	_, currState = adjudicator.run([TestAgent(1), TestAgent(2)], diceRolls, None, None, False)

	return currState.position == (3, 3) \
		and currState.cashHoldings == (1444, 1496) \
		and currState.propertyStatus[3] == 1

def testBuyPropertyIfEmpty(adjudicator):
	logger.debug('Testing Property is purchased only if unowned')
	diceRolls = [[(1, 2)], [(2, 1)]]
	_, currState = adjudicator.run([TestAgent(1), TestAgent(2)], diceRolls, None, None, False)

	return currState.propertyStatus[3] == 1

def testChanceCardForCollectionFromBank(adjudicator):
	logger.debug('Testing player collects money from bank using chance cards')
	
	chanceCards = [6, 11, 15]
	resultingAmount = [1550, 1485, 1650]

	for i in range(len(chanceCards)):
		diceRolls = [[(3, 4)]]
		card = chanceCards[i]
		_, currState = Game().run([TestAgent(1), TestAgent(2)], diceRolls, [card], None, False)
		if currState.cashHoldings != (resultingAmount[i], 1500):
			return False
	return True

def testCommunityCards(adjudicator):
	logger.debug('Testing player settles money using community cards')
	
	communityCards = [1, 2, 3, 7, 8, 9, 10, 11, 12, 14, 15]
	resultingAmount = [1700, 1450, 1550, 1600, 1520, 1600, 1450, 1450, 1525, 1510, 1600]

	for i in range(len(communityCards)):
		diceRolls = [[(1, 1)]]
		card = communityCards[i]
		_, currState = Game().run([TestAgent(1), TestAgent(2)], diceRolls, None, [card], False)
		if currState.cashHoldings != (resultingAmount[i], 1500):
			return False
	return True

tests = [
	testJailOnDoubles,
	testJailOnGoToJailCell,
	testGetOutOfJailUsingDoubles,
	testChanceCardForCollectionFromBank,
	testCommunityCards,
	testHouseGettingBuilt,
	testBuyPropertyIfEmpty,
	testPayRentIfNotOwned,
	testPayTaxes
]

def runTests():
	failedTests = []
	for test in tests:
		adjudicator = Game()
		logger.debug('\n\n\nSTARTING NEW TEST CASE\n')
		result = test(adjudicator)
		if not result:
			failedTests.append(test.__name__)
	if len(failedTests) == 0: 
		print("All tests passed!")
	else:
		print("Following tests failed" + str(failedTests))

runTests()