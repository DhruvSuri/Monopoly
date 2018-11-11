#! /usr/bin/env python
import Constant as constant
import json

class Board:
		
	def __init__(self):
		print('Init of Board')
		self.boardConfig = self.initializeBoardConfig()

		# Excluding JAIL index
		self.totalBoardCells = len(self.boardConfig) - 1

	def initializeBoardConfig(self):
		with open('BoardConfig.json', 'r') as f:
			config = json.load(f)
		# print(config)
		return config