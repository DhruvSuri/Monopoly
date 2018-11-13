#! /usr/bin/env python
import Constant as constant
from logger import logger
from Dice import Dice
from Board import Board
from State import State
from copy import deepcopy
import numpy as np

class Game:
	def __init__(self, players):
		# Board initialization
		self.board = Board()

		self.players = players

		# Dice initialization
		self.dices = []
		for seed in constant.DICE_SEEDS:
			self.dices.append(Dice(seed))

		# Current State
		propertyStatusArr = [constant.INITIAL_PROPERTY_STATUS for x in range(constant.PROPERTY_COUNT)]
		
		self.curState = State(constant.TURN_INIT, \
							constant.INITIAL_DICE_ROLL, \
							constant.INITIAL_POSITION, \
							constant.INITIAL_CASH_HOLDINGS, \
							constant.BANK_MONEY, \
							propertyStatusArr)

		# State History
		self.stateHist = []

	def run(self):
		logger.info("Game started!")

		for moveCount in range(constant.MAX_MOVES):
			logger.info("--------------Move: %d-------------", moveCount + 1)

			# Turn calculation
			turn = self.curState.turn + 1
			turnPlayerId = (turn % constant.MAX_PLAYERS)
			logger.info("Player %d turn", turnPlayerId)

			isJailed, diceRolls, totalMoves = self.diceRolls()

			if isJailed:
				logger.info("Player: %d landed in jail", turnPlayerId)
				self.landInJail(turnPlayerId, self.curState)
			else:
				# Calculating new position
				positionList = list(self.curState.position)
				positionList[turnPlayerId] = (positionList[turnPlayerId] + totalMoves) % self.board.totalBoardCells
				position = tuple(positionList)
				logger.info("Moving total %s moves. New position: %s", str(totalMoves), str(position))

			
			# Forming new current state
			self.curState.turn = turn
			self.curState.diceRoll = diceRolls
			self.curState.position = position

			# Make a move
			self.runPlayerOnState(turnPlayerId, self.curState)

			#broadcast state
			self.broadcastState(self.players, self.curState)
		
		logger.info("\n\nGame End")
		logger.info("Final Property Status: %s", str(self.curState.propertyStatus))
		
		for idx, cashHolding in enumerate(self.curState.cashHoldings):
			logger.info("Player %d cash holdings: %d", idx, cashHolding)

		logger.info("Total Money in the bank: %d", self.curState.bankMoney)

	# This needs to be change to match what is described in the API doc.
	# Needs to return an action which player is going to
	def runPlayerOnState(self, playerId, curState):
		# cur_state - property_status
		logger.info("Player %d making move!!", playerId)

		# ToDo: Model buy properly. Figure out build_cost and price. Current logic is wrong
		# ToDo: Model rent
		# ToDo: Model getting out of JAIL
		# ToDo: Model Chance card
		# ToDo: Model building house, hotels
		# ToDo: Model BSMT

		# Buying Property
		self.handleBuy(playerId, curState)

	# Using players as an argument to extend it to multiple players as well.
	def broadcastState(self, players, curState):
		for player in players:
			player.receiveState(deepcopy(curState))
		
	def handleBuy(self, playerId, curState):
		position = curState.position[playerId]
		propertyJson = self.board.boardConfig[str(position)]

		if (self.isPropertyEmpty(curState, position) \
			and self.isPropertyBuyable(propertyJson) \
			and self.isPlayerEligibleToBuyProperty(curState, playerId, propertyJson) \
			and self.players[playerId].buyProperty(curState)):

			# Update Property Status
			curState.propertyStatus[position] = self.getPropertyStatus(playerId)
			
			# Update cash holdings of Player
			newCashHolding = list(curState.cashHoldings)
			newCashHolding[playerId] = curState.cashHoldings[playerId] - propertyJson["rent_hotel"]
			curState.cashHoldings = tuple(newCashHolding)

			# Update Total Money
			curState.bankMoney = curState.bankMoney + propertyJson["rent_hotel"]

			logger.info("Property %s purchased by Player: %d. Player cash holding: %d", \
				str(propertyJson["name"]), playerId, curState.cashHoldings[playerId])

	def landInJail(self, playerId, currState):
		positionList = list(currState.position)
		positionList[playerId] = -1
		currState.position = tuple(positionList)

	def getPropertyStatus(self, playerId):
		# Define the complete enum for buying property and house
		if (playerId == 0):
			return 1
		else: 
			return -1

	def isPropertyEmpty(self, curState, position):
		return curState.propertyStatus[position] == 0

	def isPropertyBuyable(self, propertyJson):
		return propertyJson["rent_hotel"] > 0

	def isPlayerEligibleToBuyProperty(self, curState, playerId, propertyJson):
		return curState.cashHoldings[playerId] >= propertyJson["rent_hotel"]

	def diceRolls(self):
		# Returns [isJailed, rolls, totalMoves]
		# totalMoves is 0 when isJailed is True
		
		isJailed = True
		totalMoves = 0
		rollsHist = []
		for _ in range(constant.MAX_ROLLS_FOR_JAIL):
			
			rolls = []
			for dice in self.dices:
				rolls.append(dice.roll())
			logger.info("Dice Roll: %s", str(rolls))
			
			rollsHist.append(tuple(rolls))
			
			totalMoves = totalMoves + np.sum(rolls)
			
			uniqueRolls = np.unique(rolls)
			if len(uniqueRolls) != 1 or uniqueRolls[0] != constant.DICE_ROLL_MAX_VALUE:
				isJailed = False
				break
		
		if isJailed:
			totalMoves = 0

		return [isJailed, rollsHist, totalMoves]
