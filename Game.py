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
	def __init__(self):

		# Board initialization
		self.board = Board()
		
		# Initialize Cards
		self.initCards()

		# Dice initialization
		self.initDice()

		# Current State
		self.initState()

		# Registering Board Cell Handlers
		self.registerBoardCellHandlers()

	def initCards(self):
		# Chance cards
		self.chanceCardsNumbers = [i for i in range(0, 16)]
		np.random.shuffle(self.chanceCardsNumbers)
		
		# Community Chest cards
		self.communityCardsNumbers = [i for i in range(0, 16)]
		np.random.shuffle(self.communityCardsNumbers)

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

	# Register handlers based on the class
	def registerBoardCellHandlers(self):
		self.boardCellHandlers = dict()
		self.boardCellHandlers["GoToJail"] = self.handleCellGoToJail
		self.boardCellHandlers["Tax"] = self.handleCellPayTax
		self.boardCellHandlers["Street"] = self.handleCellStreet
		self.boardCellHandlers["RailRoad"] = self.handleCellRailRoad
		self.boardCellHandlers["Utility"] = self.handleCellUtility
		self.boardCellHandlers["Chance"] = self.handleChanceCard
		self.boardCellHandlers["Chest"] = self.handleCommunityCard

	def run(self, \
			players, \
			fixedDiceRolls = None, \
			fixedChanceCards = None, \
			fixedCommunityChestCards = None):
		self.players = players
		self.fixedDiceRolls = fixedDiceRolls
		
		if not fixedChanceCards == None:
			self.chanceCardsNumbers = fixedChanceCards
		
		if not fixedCommunityChestCards == None:
			self.communityCardsNumbers = fixedCommunityChestCards

		logger.info("Game started!")

		for moveCount in range(constant.MAX_MOVES):
			if (not self.fixedDiceRolls == None) and len(self.fixedDiceRolls) == 0:
				break

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

			# Broadcast state to all the players
			self.broadcastState(self.currState, self.players)

			# Maintaining state history
			self.stateHist.append(deepcopy(self.currState))
		
		logger.info("\nGame End\n")
		self.displayState(self.currState, self.players)
		winners = self.calculateWinner(self.currState, self.players)

		return winners, self.currState

	# Using players as an argument to extend it to multiple players as well.
	def broadcastState(self, currState, players):
		for player in players:
			player.receiveState(deepcopy(currState))

	def handleBSMT(self, currState, players):
		for player in players:
			action = player.getBMSTDecision(currState)
			# TODO: Execute the action

	# Turn calculation and update state
	def handleTurn(self, currState):
		currState.turn = currState.turn + 1
		return currState.turn % constant.MAX_PLAYERS

	def handleDiceRolls(self, currState, players, turnPlayerId):
		rollsHist = []
		if not self.fixedDiceRolls == None:
			rollsHist = self.fixedDiceRolls.pop(0)
		else:
			for _ in range(constant.MAX_ROLLS_FOR_JAIL):
			
				rolls = []
				for dice in self.dices:
					rolls.append(dice.roll())
			
				rollsHist.append(tuple(rolls))
						
				uniqueRolls = np.unique(rolls)
				if currState.isPlayerInJail(turnPlayerId) or len(uniqueRolls) != 1:
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

			# Reset position of player to GO if in Jail and getting out now
			if currentPosition == constant.IN_JAIL_INDEX:
				currentPosition = constant.GO_CELL

			totalMoves = np.sum(currState.diceRoll)
			newPosition = (currentPosition + totalMoves) % self.board.totalBoardCells

		self.movePlayer(currState, turnPlayerId, newPosition)

	def shouldGoToJailFromDiceRoll(self, currState, players, turnPlayerId):
		uniqueLastRoll = np.unique(currState.diceRoll[-1])
		if currState.position[turnPlayerId] == constant.IN_JAIL_INDEX:
			return len(uniqueLastRoll) != 1
		
		return len(currState.diceRoll) == 3 and len(uniqueLastRoll) == 1

	def movePlayer(self, currState, playerId, newPosition):
		positionList = list(currState.position)
		positionList[playerId] = newPosition
		 
		currState.position = tuple(positionList)

	def displayState(self, currState, players):
		logger.info("Final Property Status:")
		for idx in range(1, len(currState.propertyStatus) - 2):
			propertyName = self.board.getPropertyName(idx)
			logger.info("Property %s: %d", propertyName, currState.propertyStatus[idx])

		logger.info("Total Money in the bank: %d", currState.bankMoney)

	def calculateWinner(self, currState, players):
		wealthList = []
		for i, player in enumerate(players):
			wealth = currState.cashHoldings[i]

			for j in range(1, len(currState.propertyStatus) - 2):
				if i == currState.getPropertyOwner(j):
					wealth = wealth \
						+ (np.abs(currState.getPropertyStatus(j)) - 1) * self.board.getPropertyBuildCost(j) \
						+ self.board.getPropertyPrice(j)
			wealthList.append(wealth)

			logger.info("Player %d total wealth: %d", player.id, wealth)

		winners = [players[i].id for i, x in enumerate(wealthList) if x == np.max(wealthList)]

		if len(winners) > 1:
			logger.info("Match tied between players: %s", str(winners))
		else:
			logger.info("Winner is: %d", winners[0])

		return winners

	# Identify and Execute proper handler associated to cell class
	def handleBoardCell(self, currState, players, turnPlayerId):
		playerPosition = currState.position[turnPlayerId]
		boardCellClass = self.board.getPropertyClass(playerPosition)
		if boardCellClass in self.boardCellHandlers:
			handler = self.boardCellHandlers[boardCellClass]
			handler(currState, players, turnPlayerId)
		else:
			logger.debug("No handler specified")

	def handleCellGoToJail(self, currState, players, turnPlayerId):
		logger.debug("handleCellGoToJail called")
		if currState.position[turnPlayerId] == constant.IN_JAIL_INDEX:
			logger.info("Player: %d staying in jail", players[turnPlayerId].id)
		else:
			self.movePlayer(currState, turnPlayerId, constant.IN_JAIL_INDEX)
			logger.info("Player: %d landed in jail", players[turnPlayerId].id)
	
	def handleCellPayTax(self, currState, players, turnPlayerId):
		logger.debug("handleCellPayTax called")
		
		playerPosition = currState.position[turnPlayerId]
		tax = self.board.getPropertyTax(playerPosition)
		currState.bankMoney = currState.bankMoney + tax
		currState.updateCashHolding(turnPlayerId, -1 * tax)
	
	def handleCellStreet(self, currState, players, turnPlayerId):
		logger.debug("handleCellStreet called")

		position = currState.position[turnPlayerId]
		owner = self.currState.getPropertyOwner(position)

		if currState.isPropertyEmpty(position):
			# Buy Property
			self.buyProperty(currState, turnPlayerId, position)
		elif not (turnPlayerId == owner):
			# Pay Rent
			propertyStatus = np.abs(currState.getPropertyStatus(position))
			rent = self.board.getPropertyRent(position)[propertyStatus - 1]

			currState.updateCashHolding(owner, rent)
			currState.updateCashHolding(turnPlayerId, -1 * rent)

			logger.info("Player %d paid %d rent to Player %d", \
				players[turnPlayerId].id, players[owner].id, rent)
		else: 
			#Greedy Buy house. Have to be moved to BSMT
			self.buyHouse(currState, turnPlayerId, position)

	def handleCellRailRoad(self, currState, players, turnPlayerId):
		self.handleCellStreet(currState, players, turnPlayerId)

	def handleCellUtility(self, currState, players, turnPlayerId):
		self.handleCellStreet(currState, players, turnPlayerId)

	def handleChanceCard(self, currState, players, playerId):
		#TODO fill all positions.
		
		cardId = self.chanceCardsNumbers.pop(0)
		self.chanceCardsNumbers.append(cardId)
		card = self.board.getChanceCard(cardId)
		logger.info("Running Chance card")

		positionList = list(currState.position)
		currPosition = positionList[playerId]
		
		if card["type"] == constant.SETTLE_AMOUNT_WITH_BANK:
			self.handleCollectMoneyFromBank(currState, playerId,int(card["money"]))
		elif card["type"] == constant.GET_OUT_OF_JAIL:
			self.handleGetOutOfJail(currState, self.players, playerId)
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


	def handleCommunityCard(self, currState, players, playerId):
		cardId = self.communityCardsNumbers.pop(0)
		card = self.board.getChanceCard(cardId)
		self.communityCardsNumbers.append(cardId)
		logger.info("Running Community Card: %d", cardId)

		positionList = list(currState.position)
		currPosition = positionList[playerId]

		if card["type"] == constant.SETTLE_AMOUNT_WITH_BANK:
			self.handleCollectMoneyFromBank(currState, playerId,int(card["money"]))
		elif card["type"] == constant.GET_OUT_OF_JAIL:
			self.handleGetOutOfJail(currState, players, playerId)
		else:
			logger.info("Community Chest card not modelled for this position")
		#TODO model all cards
		self.movePlayer(currState, playerId, currPosition)
		
	def buyProperty(self, currState, playerId, propertyPosition):
		price = self.board.getPropertyPrice(propertyPosition)

		if (currState.cashHoldings[playerId] >= price \
			and self.players[playerId].buyProperty(currState)):

			currState.updatePropertyStatus(propertyPosition, playerId)
			currState.updateCashHolding(playerId, -1 * price)
			currState.bankMoney = currState.bankMoney + price

			logger.info("Property %s purchased by Player: %d. Player cash holding: %d", \
				self.board.getPropertyName(propertyPosition), playerId+1, currState.cashHoldings[playerId])

	def buyHouse(self, currState, playerId, position):
		monopolyGroup = self.board.getMonopolyGroup(position)
		price = self.board.getPropertyBuildCost(position)

		if (currState.cashHoldings[playerId] >= price \
			and currState.allHouseConditionsSatisfied(playerId, position, monopolyGroup)):
			#TODO Add BMST decision
			
			currState.updateHouseStatus(playerId, position)
			currState.updateCashHolding(playerId, -1 * price)

			logger.info("House built on property %s by Player: %d. Player cash holding: %d", \
				self.board.getPropertyName(position), playerId, currState.cashHoldings[playerId])

	def handleGetOutOfJail(self, currState, players, turnPlayerId):
		if currState.position[turnPlayerId] == constant.IN_JAIL_INDEX:
			self.movePlayer(currState, turnPlayerId, constant.GO_CELL)
			logger.info("Player: %d moved out of jail", players[turnPlayerId].id)

	def handleCollectMoneyFromBank(self, currState, playerId, amount):
		cashHolding = list(currState.cashHoldings)
		cashHolding[playerId] = currState.cashHoldings[playerId] + amount
		currState.cashHoldings = tuple(cashHolding)
