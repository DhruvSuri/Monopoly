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
		self.communityCardsNumbers = [i for i in range(0, 16)]
		np.random.shuffle(self.communityCardsNumbers)

		self.chanceCards = self.initializeCards(constant.CHANCE_CARD_FILE_NAME)
		self.communityCards = self.initializeCards(constant.COMMUNITY_CARDS_FILE_NAME)

		# Dice initialization
		self.initDice()

		# Current State
		self.initState()

		# Registering Board Cell Handlers
		self.registerBoardCellHandlers()

	def initDice(self):
		self.dices = []
		for seed in constant.DICE_SEEDS:
			self.dices.append(Dice(seed))

	def initState(self):
		propertyStatus = [constant.INITIAL_PROPERTY_STATUS for x in range(constant.PROPERTY_COUNT)]
		
		self.currState = State(constant.TURN_INIT, \
							constant.INITIAL_DICE_ROLL, \
							constant.INITIAL_POSITION, \
							constant.INITIAL_CASH_HOLDINGS, \
							constant.BANK_MONEY, \
							propertyStatus)

		# State History
		self.stateHist = []

	def registerBoardCellHandlers(self):
		self.boardCellHandlers = dict()
		self.boardCellHandlers["GoToJail"] = self.handleCellGoToJail
		self.boardCellHandlers["Tax"] = self.handleCellPayTax

	def run(self):
		logger.info("Game started!")

		for moveCount in range(constant.MAX_MOVES):
			logger.info("--------------Move: %d-------------", moveCount + 1)

			# Execute BSMT for all players
			self.handleBSMT(self.currState, self.players)
			
			# Turn calculation
			turnPlayerId = self.handleTurn(self.currState)
			logger.info("Player %d turn", self.players[turnPlayerId].id)

			# Dice Rolls
			diceRolls = self.handleDiceRolls(self.currState, self.players, turnPlayerId)
			logger.info("Dice Rolls: %s", str(diceRolls))

			# Update Position based on dice roll
			self.handleNewPosition(self.currState, self.players, turnPlayerId)
			logger.info("New position: %s", str(self.currState.position))
			
			# Calling handler of board cell
			self.handleBoardCell(self.currState, self.players, turnPlayerId)
			logger.info("New cash holding: %s", str(self.currState.cashHoldings))

			# Make a move
			self.runPlayerOnState(turnPlayerId, self.currState)

			# Broadcast state to all the players
			self.broadcastState(self.currState, self.players)
		
		logger.info("\nGame End\n")
		self.displayState(self.currState, self.players)

	def runPlayerOnState(self, playerId, currState):
		position = currState.position[playerId]

		if self.board.isPropertyBuyable(str(position)):
			if self.isPropertyEmpty(currState, position):
				self.handleBuy(playerId, currState)
			elif not playerId == self.getPropertyOwner(currState, position):
				self.handleRent(playerId, currState)
		elif self.board.isChanceCardPosition(str(position)):
			self.runChanceCard(currState, playerId)
		elif self.board.isCommunityCardPosition(str(position)):
			self.runCommunityCard(currState, playerId)
		else:
			logger.debug("Board Position not modelled")

		# ToDo: Model getting out of JAIL		

	# Using players as an argument to extend it to multiple players as well.
	def broadcastState(self, currState, players):
		for player in players:
			player.receiveState(deepcopy(currState))

	def handleRent(self, playerId, currState):
		position = currState.position[playerId]
		propertyJson = self.board.boardConfig[str(position)]

		ownerId = self.getPropertyOwner(currState, position)
		
		# ToDo: Model Rent based on house, hotels etc.
		rent = propertyJson["rent"]
		
		newCashHolding = list(currState.cashHoldings)
		newCashHolding[ownerId] = currState.cashHoldings[ownerId] + rent

		# ToDo: Handle what to do in case of not enough money
		newCashHolding[playerId] = currState.cashHoldings[playerId] - rent

		logger.info("Rent paid by Player: %d is %d", playerId, rent)
		currState.cashHoldings = tuple(newCashHolding)
		
	def handleBuy(self, playerId, currState):
		position = currState.position[playerId]
		propertyJson = self.board.boardConfig[str(position)]

		if (currState.cashHoldings[playerId] >= propertyJson["price"] \
			and self.players[playerId].buyProperty(currState)):

			# Update Property Status
			currState.propertyStatus[position] = self.getPropertyStatus(playerId)
			
			# Update cash holdings of Player
			newCashHolding = list(currState.cashHoldings)
			newCashHolding[playerId] = currState.cashHoldings[playerId] - propertyJson["price"]
			currState.cashHoldings = tuple(newCashHolding)

			# Update Total Money
			currState.bankMoney = currState.bankMoney + propertyJson["price"]

			logger.info("Property %s purchased by Player: %d. Player cash holding: %d", \
				str(propertyJson["name"]), playerId, currState.cashHoldings[playerId])

	def landInJail(self, playerId, currState):
		if currState.position[playerId] == constant.IN_JAIL_INDEX:
			logger.info("Player: %d staying in jail", playerId)
		else:
			logger.info("Player: %d landed in jail", playerId)
			positionList = list(currState.position)
			positionList[playerId] = constant.IN_JAIL_INDEX
			currState.position = tuple(positionList)

	def getPropertyStatus(self, playerId):
		# Define the complete enum for buying property and house
		if (playerId == 0):
			return 1
		else: 
			return -1

	def getPropertyOwner(self, currState, propertyPosition):
		if currState.propertyStatus[propertyPosition] > 0:
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

	def runChanceCard(self, currState, playerId):
		#TODO fill all positions.
		
		cardId = self.chanceCardsNumbers.pop(0)
		self.chanceCardsNumbers.append(cardId)
		card = self.chanceCards[cardId]
		logger.info("Running Chance card")

		positionList = list(currState.position)
		currPosition = positionList[playerId]

		
		if card["type"] == constant.SETTLE_AMOUNT_WITH_BANK:
			self.handleCollectMoneyFromBank(currState, playerId,int(card["money"]))
		elif card["type"] == constant.GET_OUT_OF_JAIL:
			self.handleGetOutOfJail(currState, playerId)
		elif cardId == 0:
			#Move to Go
			currPosition = constant.GO_CELL
			self.handleCollectMoneyFromBank(currState, playerId, 200)
		
		elif cardId == 8:
			#Only 1 case for -3 moves. Never makes position -ve.
			currPosition = currPosition - 3
		else:
			logger.info("Chance card not modelled for this position")

		#TODO model all cards
		self.movePlayer(currState, playerId, currPosition)


	def runCommunityCard(self, currState, playerId):
		cardId = self.communityCardsNumbers.pop(0)
		card = self.communityCards[cardId]
		self.communityCardsNumbers.append(cardId)
		logger.info("Running Community Card: %d", cardId)

		positionList = list(currState.position)
		currPosition = positionList[playerId]

		if card["type"] == constant.SETTLE_AMOUNT_WITH_BANK:
			self.handleCollectMoneyFromBank(currState, playerId,int(card["money"]))
		elif card["type"] == constant.GET_OUT_OF_JAIL:
			self.handleGetOutOfJail(currState, playerId)
		else:
			logger.info("Community Chest card not modelled for this position")
		#TODO model all cards
		self.movePlayer(currState, playerId, currPosition)

	def handleBSMT(self, currState, players):
		for player in players:
			action = player.getBMSTDecision(currState)
			# ToDo: Execute the action

	# Turn calculation and update state
	def handleTurn(self, currState):
		currState.turn = currState.turn + 1
		return currState.turn % constant.MAX_PLAYERS

	def handleDiceRolls(self, currState, players, turnPlayerId):
		rollsHist = []
		for _ in range(constant.MAX_ROLLS_FOR_JAIL):
			
			rolls = []
			for dice in self.dices:
				rolls.append(dice.roll())
			
			rollsHist.append(tuple(rolls))
						
			uniqueRolls = np.unique(rolls)
			if currState.isPlayerInJail(turnPlayerId) \
				or len(uniqueRolls) != 1 \
				or uniqueRolls[0] != constant.DICE_ROLL_MAX_VALUE:
				break

		# Update current state with the dice roll
		self.currState.diceRoll = rollsHist

		return rollsHist

	def handleNewPosition(self, currState, players, turnPlayerId):
		if self.shouldGoToJailFromDiceRoll(currState, players, turnPlayerId):
			newPosition = constant.IN_JAIL_INDEX
		else:
			positionList = list(self.currState.position)
			currentPosition = positionList[turnPlayerId]
			
			# Doubt
			# Reset position of player to GO if in Jail
			if currentPosition == constant.IN_JAIL_INDEX:
				currentPosition = constant.GO_CELL

			totalMoves = np.sum(currState.diceRoll)
			newPosition = (currentPosition + totalMoves) % self.board.totalBoardCells

		self.movePlayer(currState, turnPlayerId, newPosition)

	def shouldGoToJailFromDiceRoll(self, currState, players, turnPlayerId):
		uniqueLastRoll = np.unique(currState.diceRoll[-1])
		if currState.position[turnPlayerId] == constant.IN_JAIL_INDEX:
			return len(uniqueLastRoll) != 1
		
		return len(currState.diceRoll) == 3 \
			and len(uniqueLastRoll) == 1 \
			and uniqueLastRoll[0] == constant.DICE_ROLL_MAX_VALUE

	def movePlayer(self, currState, playerId, newPosition):
		positionList = list(currState.position)
		positionList[playerId] = newPosition
		 
		currState.position = tuple(positionList)

	def updateCashHolding(self, currState, playerId, cashToAdd):
		newCashHolding = list(currState.cashHoldings)
		newCashHolding[playerId] = currState.cashHoldings[playerId] + cashToAdd
		currState.cashHoldings = tuple(newCashHolding)

	def displayState(self, currState, players):		
		for idx, cashHolding in enumerate(currState.cashHoldings):
			logger.info("Player %d cash holdings: %d", players[idx].id, cashHolding)
		logger.info("Total Money in the bank: %d", currState.bankMoney)

		logger.info("Final Property Status:")
		for idx in range(1, len(currState.propertyStatus) - 2):
			propertyName = self.board.getPropertyName(str(idx))
			logger.info("Property %s: %d", propertyName, currState.propertyStatus[idx])

	def isPropertyEmpty(self, currState, position):
		return currState.propertyStatus[position] == 0

	def handleCollectMoneyFromBank(self, currState, playerId, amount):
		cashHolding = list(currState.cashHoldings)
		cashHolding[playerId] = currState.cashHoldings[playerId] + amount
		currState.cashHoldings = tuple(cashHolding)

		#TODO: If banks goes below 0 :(
		currState.bankMoney = currState.bankMoney - amount

	def handleBoardCell(self, currState, players, turnPlayerId):
		playerPosition = currState.position[turnPlayerId]
		boardCellClass = self.board.getPropertyClass(str(playerPosition))
		if boardCellClass in self.boardCellHandlers:
			handler = self.boardCellHandlers[boardCellClass]
			handler(currState, players, turnPlayerId)
		else:
			logger.debug("No handler specified")

	#Doubt : duplicate of landInJail
	def handleCellGoToJail(self, currState, players, turnPlayerId):
		logger.debug("handleCellGoToJail called")
		if currState.position[turnPlayerId] == constant.IN_JAIL_INDEX:
			logger.info("Player: %d staying in jail", players[turnPlayerId].id)
		else:
			self.movePlayer(currState, turnPlayerId, constant.IN_JAIL_INDEX)
			logger.info("Player: %d landed in jail", players[turnPlayerId].id)
	
	def handleGetOutOfJail(self, currState, turnPlayerId):
		if currState.position[turnPlayerId] == constant.IN_JAIL_INDEX:
			self.movePlayer(currState, turnPlayerId, constant.GO_CELL)
			logger.info("Player: %d moved out of jail", players[turnPlayerId].id)

	def handleCellPayTax(self, currState, players, turnPlayerId):
		logger.debug("handleCellPayTax called")
		
		playerPosition = currState.position[turnPlayerId]
		tax = self.board.getPropertyTax(str(playerPosition))
		self.updateCashHolding(currState, turnPlayerId, -1 * tax)