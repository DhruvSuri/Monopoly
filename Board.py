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
		return self.boardConfig[idx]["price"] > 0