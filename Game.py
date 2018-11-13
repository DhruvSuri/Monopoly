#! /usr/bin/env python
import Constant as constant
from logger import logger
from Dice import Dice
from Board import Board
from State import State
from copy import deepcopy

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
		propertyStatusArr = [0 for x in range(constant.PROPERTY_COUNT)]
		self.curState = State(constant.TURN_INIT, constant.INITIAL_DICE_ROLL, \
		constant.INITIAL_POSITION, constant.INITIAL_CASH_HOLDINGS, constant.BANK_MONEY, \
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

			isJailed, diceRollTupple, totalMoves = self.diceRolls()

			if(isJailed):
				logger.info("Player: %s landed in jail", str(turnPlayerId))
				self.landInJail(turnPlayerId, self.curState)
			else:
				# Calculating new position
				positionList = list(self.curState.position)
				positionList[turnPlayerId] = (positionList[turnPlayerId] + totalMoves) % self.board.totalBoardCells
				position = tuple(positionList)
				logger.info("Moving total %s moves. New position: %s", str(totalMoves), str(position))

			
			# Forming new current state
			self.curState.turn = turn
			self.curState.dice_roll = diceRollTupple
			self.curState.position = position

			# Make a move
			self.runPlayerOnState(turnPlayerId, self.curState)

			#broadcast state
			self.broadcastState(self.players[0], self.players[1], self.curState)
		
		logger.info("\n\nGame End")
		logger.info("Final Property Status: %s", str(self.curState.propertyStatus))
		
		for idx, cashHolding in enumerate(self.curState.cashHoldings):
			logger.info("Player %d cash holdings: %d", idx, cashHolding)

		logger.info("Total Money in the bank: %d", self.curState.bankMoney)

	def runPlayerOnState(self, playerId, curState):
		# cur_state - property_status
		logger.info("Player %d making move!!", playerId);

		# Buying Property
		self.handleBuy(playerId, curState)

	def broadcastState(self, player0, player1, cur_state):
		player0.state = deepcopy(cur_state)
		player1.state = deepcopy(cur_state)
		
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
		#returns [is_jailed, dice_roll_tupple, total__move_count]
		rolls = []
		sum = 0

		#First roll
		for dice in self.dices:
			rolls.append(dice.roll())
		sum = rolls[0] + rolls[1]
		if(sum != 12):
			return [False, tuple(rolls), sum]

		#sencond roll
		logger.info("Die Roll = (6, 6). Rolling again")
		rolls = []
		for dice in self.dices:
			rolls.append(dice.roll())
		sum = sum + rolls[0] + rolls[1]
		if(sum != 24):
			return [False, tuple(rolls), sum]

		#third roll
		logger.info("Die Roll = (6, 6). Rolling again")
		rolls = []
		for dice in self.dices:
			rolls.append(dice.roll())
		sum = sum + rolls[0] + rolls[1]
		if(sum == 36):
			return [True, tuple(rolls), sum]
		else:
			return [False, tuple(rolls), sum]

