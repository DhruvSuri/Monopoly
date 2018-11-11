#! /usr/bin/env python
import Constant as constant
import json

class Board:
		
	def __init__(self):
		print('Init of Board')
		self.board_config = self.initialize_board_config()

		# Excluding JAIL index
		self.total_board_cells = len(self.board_config) - 1

	def initialize_board_config(self):
		with open('BoardConfig.json', 'r') as f:
			config = json.load(f)
		# print(config)
		return config