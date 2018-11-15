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
		# ToDo: Different actions needs to be modelled R, P or C
		# Currently in greedy approach modelling as P
		return ("P")

def testJailOnDoubles(adjudicator):
    diceRolls = [[(1,4)], [(5, 5), (4, 4), (3, 3)]]
    
    _, currState = adjudicator.run([TestAgent(1), TestAgent(2)], diceRolls)

    return currState.position == (5, -1)

tests = [
    testJailOnDoubles
    # testJailOnGoToJailCell
    # testGetOutOfJailUsingDoubles
    # testGetOutOfJailUsingChanceCard
    # testGetOutOfJailUsingCommunityCard
    # testHouseGettingBuilt
    # testBuyPropertyIfEmpty
    # testPayRentIfNotOwned
    # testPayTaxes
]

def runTests():
    allPassed = True
    adjudicator = Game()
    for test in tests:
        result = test(adjudicator)
        if not result:
            print(test.__name__ + " failed!")
            allPassed = False
    if allPassed: print("All tests passed!")

runTests()