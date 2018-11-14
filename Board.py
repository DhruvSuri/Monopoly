#! /usr/bin/env python
import Constant as constant
from logger import logger
import json

class Board:
		
	def __init__(self):
		self.boardConfig = self.initializeBoardConfig()

		# Excluding JAIL index
		self.totalBoardCells = len(self.boardConfig) - 1

		logger.info('Board initialized')

	def initializeBoardConfig(self):
		with open('BoardConfig.json', 'r') as f:
			config = json.load(f)
		# print(config)
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
		return self.boardConfig[str(idx)]["price"]