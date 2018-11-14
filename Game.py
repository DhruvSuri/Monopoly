#! /usr/bin/env python
import Constant as constant
from logger import logger
from Dice import Dice
from Board import Board
from State import State
from copy import deepcopy
import numpy as np
import json

class Game:
	def __init__(self, players):
		# Board initialization
		self.board = Board()

		self.players = players
		
		# Initialize Cards
		self.chanceCardsNumbers = [i for i in range(0, 16)]
		np.random.shuffle(self.chanceCardsNumbers)
		self.communityCardsNumbers = [i for i in range(0, 17)]
		np.random.shuffle(self.communityCardsNumbers)

		self.chanceCards = self.initializeCards(constant.CHANCE_CARD_FILE_NAME)
		self.communityCards = self.initializeCards(constant.COMMUNITY_CARDS_FILE_NAME)


		# Dice initialization
		self.dices = []
		for seed in constant.DICE_SEEDS:
			self.dices.append(Dice(seed))

		# Current State
		propertyStatus = [constant.INITIAL_PROPERTY_STATUS for x in range(constant.PROPERTY_COUNT)]
		
		self.curState = State(constant.TURN_INIT, \
							constant.INITIAL_DICE_ROLL, \
							constant.INITIAL_POSITION, \
							constant.INITIAL_CASH_HOLDINGS, \
							constant.BANK_MONEY, \
							propertyStatus)

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

			isJailed, diceRolls, totalMoves = self.diceRolls(self.curState, turnPlayerId)

			if isJailed:
				self.landInJail(turnPlayerId, self.curState)
			else:
				# Calculating new position
				positionList = list(self.curState.position)
				currentPosition = positionList[turnPlayerId]
				
				# Reset position of player to GO if in Jail
				if currentPosition == constant.IN_JAIL_INDEX:
					currentPosition = constant.GO_CELL
				newPosition = (currentPosition + totalMoves) % self.board.totalBoardCells
				
				# Send Player to Jail if reach on go to jail cell
				if newPosition == constant.GO_TO_JAIL_CELL:
					positionList[turnPlayerId] = constant.IN_JAIL_INDEX
				else:
					positionList[turnPlayerId] = newPosition
				position = tuple(positionList)
				logger.info("Moving total %d moves. New position: %s", totalMoves, str(position))

			
			# Forming new current state
			self.curState.turn = turn
			self.curState.diceRoll = diceRolls
			self.curState.position = position

			# Execute BSMT for all players
			self.executeBSMT(self.players, self.curState)
			
			# Make a move
			self.runPlayerOnState(turnPlayerId, self.curState)

			# Broadcast state to all the players
			self.broadcastState(self.players, self.curState)
		
		logger.info("\n\nGame End")
		logger.info("Final Property Status: %s", str(self.curState.propertyStatus))
		
		for idx, cashHolding in enumerate(self.curState.cashHoldings):
			logger.info("Player %d cash holdings: %d", idx, cashHolding)

		logger.info("Total Money in the bank: %d", self.curState.bankMoney)

	def runPlayerOnState(self, playerId, curState):
		logger.info("Player %d making move!!", playerId)

		position = curState.position[playerId]
		propertyJson = self.board.boardConfig[str(position)]

		if self.isPropertyBuyable(propertyJson):
			if self.isPropertyEmpty(curState, position):
				self.handleBuy(playerId, curState)
			elif not playerId == self.getPropertyOwner(curState, position):
				self.handleRent(playerId, curState)
			else:
				# ToDo: Model building house, hotels
				pass

		# ToDo: Model getting out of JAIL
		# ToDo: Model Chance card		

	# Using players as an argument to extend it to multiple players as well.
	def broadcastState(self, players, curState):
		for player in players:
			player.receiveState(deepcopy(curState))

	def handleRent(self, playerId, curState):
		position = curState.position[playerId]
		propertyJson = self.board.boardConfig[str(position)]

		ownerId = self.getPropertyOwner(curState, position)
		
		# ToDo: Model Rent based on house, hotels etc.
		rent = propertyJson["rent"]
		
		newCashHolding = list(curState.cashHoldings)
		newCashHolding[ownerId] = curState.cashHoldings[ownerId] + rent

		# ToDo: Handle what to do in case of not enough money
		newCashHolding[playerId] = curState.cashHoldings[playerId] - rent

		logger.info("Rent paid by Player: %d is %d", playerId, rent)
		curState.cashHoldings = tuple(newCashHolding)
		
	def handleBuy(self, playerId, curState):
		position = curState.position[playerId]
		propertyJson = self.board.boardConfig[str(position)]

		if (curState.cashHoldings[playerId] >= propertyJson["price"] \
			and self.players[playerId].buyProperty(curState)):

			# Update Property Status
			curState.propertyStatus[position] = self.getPropertyStatus(playerId)
			
			# Update cash holdings of Player
			newCashHolding = list(curState.cashHoldings)
			newCashHolding[playerId] = curState.cashHoldings[playerId] - propertyJson["price"]
			curState.cashHoldings = tuple(newCashHolding)

			# Update Total Money
			curState.bankMoney = curState.bankMoney + propertyJson["price"]

			logger.info("Property %s purchased by Player: %d. Player cash holding: %d", \
				str(propertyJson["name"]), playerId, curState.cashHoldings[playerId])

	def landInJail(self, playerId, curState):
		if curState.position[playerId] == constant.IN_JAIL_INDEX:
			logger.info("Player: %d staying in jail", playerId)
		else:
			logger.info("Player: %d landed in jail", playerId)
			positionList = list(curState.position)
			positionList[playerId] = constant.IN_JAIL_INDEX
			curState.position = tuple(positionList)

	def getPropertyStatus(self, playerId):
		# Define the complete enum for buying property and house
		if (playerId == 0):
			return 1
		else: 
			return -1

	def isPropertyEmpty(self, curState, position):
		return curState.propertyStatus[position] == 0

	def isPropertyBuyable(self, propertyJson):
		return propertyJson["price"] > 0

	def getPropertyOwner(self, curState, propertyPosition):
		if curState.propertyStatus[propertyPosition] > 0:
			return 0
		else:
			return 1

	def initializeCards(self, fileName):
		with open(fileName, 'r') as f:
			cards = json.load(f)
		np.random.shuffle(cards)
		return cards

	def drawRandomCard(self, cards):
		# np.random.shuffle(cards)
		return cards[0]

	def runChanceCard(self, currState, playerId, cardId):
		#TODO fill all positions.
		#TODO Handle cases of passing Go etc.

		positionList = list(currState.position)
		currPosition = positionList[playerId]

		if cardId == 0:
			#Move to Go
			currPosition = 0
			self.collectMoneyFromBank(currState, playerId, 200)
		
		elif cardId == 6:
			#bank pays $50
			self.collectMoneyFromBank(currState, playerId, 50)

		elif cardId == 8:
			#Only 1 case for -3 moves. Never makes position -ve.
			currPosition = currPosition - 3

		self.movePlayer(currState, playerId, currPosition)


	def runCommunityCard(self, currState, playerId, cardId):
		positionList = list(currState.position)
		currPosition = positionList[playerId]

		if cardId == 0:
			#Move to Go
			currPosition = 0
			self.collectMoneyFromBank(currState, playerId, 200)
		
		elif cardId == 1:
			#Bank error
			self.collectMoneyFromBank(currState, playerId, 50)
		
		elif cardId == 2:
			#Doctor fee
			self.collectMoneyFromBank(currState, playerId, -50)

		elif cardId == 3:
			#Stock Sale
			self.collectMoneyFromBank(currState, playerId, 50)

		self.movePlayer(currState, playerId, currPosition)

	def collectMoneyFromBank(self, currState, playerId, amount):
		cashHolding = list(currState.cashHoldings)
		cashHolding[playerId] = currState.cashHoldings[playerId] + amount
		currState.cashHoldings = tuple(newCashHolding)

		# Update Total Money
		#TODO: If banks goes below 0 :(
		currState.bankMoney = currState.bankMoney - amount


	def movePlayer(self, currState, playerId, newPosition):
		positionList = list(currState.position)
		positionList[playerId] = newPosition
		position = tuple(positionList)
		currState.position = position

	def diceRolls(self, curState, turnPlayerId):
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
			if curState.position[turnPlayerId] == constant.IN_JAIL_INDEX:
				if len(uniqueRolls) == 1:
					isJailed = False
				break
			elif len(uniqueRolls) != 1 or uniqueRolls[0] != constant.DICE_ROLL_MAX_VALUE:
				isJailed = False
				break
		
		if isJailed:
			totalMoves = 0

		return [isJailed, rollsHist, totalMoves]

	def executeBSMT(self, players, curState):
		for player in self.players:
			action = player.getBMSTDecision(curState)
			# ToDo: Execute the action
