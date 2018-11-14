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

			# Execute BSMT for all players
			self.handleBSMT(self.curState, self.players)
			
			# Turn calculation
			turnPlayerId = self.handleTurn(self.curState)
			logger.info("Player %d turn", self.players[turnPlayerId].id)

			# Dice Rolls
			diceRolls = self.handleDiceRolls(self.curState, self.players, turnPlayerId)
			logger.info("Dice Rolls: %s", str(diceRolls))

			# Update Position based on dice roll
			self.handleNewPosition(self.curState, self.players, turnPlayerId)
			logger.info("New position: %s", str(self.curState.position))
			
			# Make a move
			self.runPlayerOnState(turnPlayerId, self.curState)

			# Broadcast state to all the players
			self.broadcastState(self.curState, self.players)
		
		logger.info("\nGame End\n")
		self.displayState(self.curState, self.players)

	def runPlayerOnState(self, playerId, curState):
		position = curState.position[playerId]

		if self.board.isPropertyBuyable(str(position)):
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
	def broadcastState(self, curState, players):
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


	def handleBSMT(self, curState, players):
		for player in players:
			action = player.getBMSTDecision(curState)
			# ToDo: Execute the action

	# Turn calculation and update state
	def handleTurn(self, curState):
		curState.turn = curState.turn + 1
		return curState.turn % constant.MAX_PLAYERS

	def handleDiceRolls(self, curState, players, turnPlayerId):
		rollsHist = []
		for _ in range(constant.MAX_ROLLS_FOR_JAIL):
			
			rolls = []
			for dice in self.dices:
				rolls.append(dice.roll())
			
			rollsHist.append(tuple(rolls))
						
			uniqueRolls = np.unique(rolls)
			if curState.isPlayerInJail(turnPlayerId) \
				or len(uniqueRolls) != 1 \
				or uniqueRolls[0] != constant.DICE_ROLL_MAX_VALUE:
				break

		# Update current state with the dice roll
		self.curState.diceRoll = rollsHist

		return rollsHist

	def handleNewPosition(self, curState, players, turnPlayerId):
		if self.shouldGoToJailFromDiceRoll(curState, players, turnPlayerId):
			newPosition = constant.IN_JAIL_INDEX
		else:
			positionList = list(self.curState.position)
			currentPosition = positionList[turnPlayerId]

			# Reset position of player to GO if in Jail
			if currentPosition == constant.IN_JAIL_INDEX:
				currentPosition = constant.GO_CELL

			totalMoves = np.sum(curState.diceRoll)
			newPosition = (currentPosition + totalMoves) % self.board.totalBoardCells

		self.movePlayer(curState, turnPlayerId, newPosition)

	def shouldGoToJailFromDiceRoll(self, curState, players, turnPlayerId):
		uniqueLastRoll = np.unique(curState.diceRoll[-1])
		if curState.position[turnPlayerId] == constant.IN_JAIL_INDEX:
			return len(uniqueLastRoll) != 1
		
		return len(curState.diceRoll) == 3 \
			and len(uniqueLastRoll) == 1 \
			and uniqueLastRoll[0] == constant.DICE_ROLL_MAX_VALUE

	def movePlayer(self, curState, playerId, newPosition):
		positionList = list(curState.position)
		positionList[playerId] = newPosition
		 
		curState.position = tuple(positionList)

	def displayState(self, curState, players):		
		for idx, cashHolding in enumerate(curState.cashHoldings):
			logger.info("Player %d cash holdings: %d", players[idx].id, cashHolding)
		logger.info("Total Money in the bank: %d", curState.bankMoney)

		logger.info("Final Property Status:")
		for idx in range(len(curState.propertyStatus) - 2):
			propertyJson = self.board.boardConfig[str(idx)]
			logger.info("Property %s: %d", propertyJson["name"], curState.propertyStatus[idx])

	def isPropertyEmpty(self, curState, position):
		return curState.propertyStatus[position] == 0
