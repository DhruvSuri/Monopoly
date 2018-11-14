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
		
		self.curState = State(constant.TURN_INIT, \
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
		self.boardCellHandlers["Street"] = self.handleCellStreet

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
			
			# Calling handler of board cell
			self.handleBoardCell(self.curState, self.players, turnPlayerId)
			logger.info("New cash holding: %s", str(self.curState.cashHoldings))

			# Broadcast state to all the players
			self.broadcastState(self.curState, self.players)
		
		logger.info("\nGame End\n")
		self.displayState(self.curState, self.players)	

	# Using players as an argument to extend it to multiple players as well.
	def broadcastState(self, curState, players):
		for player in players:
			player.receiveState(deepcopy(curState))

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
		for idx in range(1, len(curState.propertyStatus) - 2):
			propertyName = self.board.getPropertyName(idx)
			logger.info("Property %s: %d", propertyName, curState.propertyStatus[idx])

	def handleBoardCell(self, curState, players, turnPlayerId):
		playerPosition = curState.position[turnPlayerId]
		boardCellClass = self.board.getPropertyClass(playerPosition)
		if boardCellClass in self.boardCellHandlers:
			handler = self.boardCellHandlers[boardCellClass]
			handler(curState, players, turnPlayerId)
		else:
			logger.debug("No handler specified")

	def handleCellGoToJail(self, curState, players, turnPlayerId):
		logger.debug("handleCellGoToJail called")
		if curState.position[turnPlayerId] == constant.IN_JAIL_INDEX:
			logger.info("Player: %d staying in jail", players[turnPlayerId].id)
		else:
			self.movePlayer(curState, turnPlayerId, constant.IN_JAIL_INDEX)
			logger.info("Player: %d landed in jail", players[turnPlayerId].id)
	
	def handleCellPayTax(self, curState, players, turnPlayerId):
		logger.debug("handleCellPayTax called")
		
		playerPosition = curState.position[turnPlayerId]
		tax = self.board.getPropertyTax(playerPosition)
		curState.updateCashHolding(turnPlayerId, -1 * tax)
	
	def handleCellStreet(self, curState, players, turnPlayerId):
		logger.debug("handleCellStreet called")

		position = curState.position[turnPlayerId]
		owner = self.curState.getPropertyOwner(position)

		if curState.isPropertyEmpty(position):
			# Buy Property
			self.buyProperty(curState, turnPlayerId, position)
		elif not (turnPlayerId == owner):
			# Pay Rent
			rent = self.board.getPropertyRent(position)

			curState.updateCashHolding(owner, rent)
			curState.updateCashHolding(turnPlayerId, -1 * rent)

			logger.info("Player %d paid %d rent", players[turnPlayerId].id, rent)
		
	def buyProperty(self, curState, playerId, propertyPosition):
		price = self.board.getPropertyPrice(propertyPosition)

		if (curState.cashHoldings[playerId] >= price \
			and self.players[playerId].buyProperty(curState)):

			curState.updatePropertyStatus(propertyPosition, playerId)
			curState.updateCashHolding(playerId, -1 * price)
			curState.bankMoney = curState.bankMoney + price

			logger.info("Property %s purchased by Player: %d. Player cash holding: %d", \
				self.board.getPropertyName(propertyPosition), playerId, curState.cashHoldings[playerId])