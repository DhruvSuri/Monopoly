#! /usr/bin/env python
import Constant as constant
import json

class Board:
		
	def __init__(self):
		print('Init of Board')
		self.board = {}
		self.board_config = self.initialize_board_config()
		self.board[constant.IN_JAIL_INDEX] = {}
		for i in range(constant.BOARD_SIZE):
			self.board[i] = {}

	def initialize_board_config(self):
		with open('BoardConfig.json', 'r') as f:
			config = json.load(f)
		# print(config)
		return config