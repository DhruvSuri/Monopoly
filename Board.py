#! /usr/bin/env python
import Constant as constant
from logger import logger
import json
import numpy as np

class Board:
		
	def __init__(self):
		self.boardConfig = self.readConfig(constant.BOARD_CONFIG_FILE)
		self.chanceCards = self.readConfig(constant.CHANCE_CARD_FILE_NAME)
		self.communityCards = self.readConfig(constant.COMMUNITY_CARDS_FILE_NAME)

		# Excluding JAIL index
		self.totalBoardCells = len(self.boardConfig) - 1

		logger.info('Board initialized')

	def readConfig(self, fileName):
		with open(fileName, 'r') as f:
			config = json.load(f)
		return config

	def isPropertyBuyable(self, idx):
		return self.boardConfig[str(idx)]["price"] > 0

	def isChanceCardPosition(self, idx):
		return self.getPropertyClass(idx) == "Chance"

	def isCommunityCardPosition(self, idx):
		return self.getPropertyClass(idx) == "Chest"

	def getPropertyName(self, idx):
		return self.boardConfig[str(idx)]["name"]

	def getPropertyClass(self, idx):
		return self.boardConfig[str(idx)]["class"]

	def getPropertyTax(self, idx):
		return self.boardConfig[str(idx)]["tax"]

	def getPropertyRent(self, idx):
		return self.boardConfig[str(idx)]["rent"]

	def getPropertyPrice(self, idx):
		if "price" in self.boardConfig[str(idx)]:
			return self.boardConfig[str(idx)]["price"]
		return 0

	def getPropertyBuildCost(self, idx):
		if "build_cost" in self.boardConfig[str(idx)]:
			return self.boardConfig[str(idx)]["build_cost"]
		return 0

	def getCommunityCard(self, idx):
		return self.communityCards[idx]
	
	def getChanceCard(self, idx):
		return self.chanceCards[idx]

	def getMonopolyGroup(self, idx):
		colorGroupName = self.boardConfig[str(idx)]["colorGroup"]
		monopolyList = []
		if colorGroupName == "None":
			return monopolyList

		for i in range(constant.BOARD_SIZE):
			if self.boardConfig[str(i)]["colorGroup"] == colorGroupName:
				monopolyList.append(i)

		return monopolyList