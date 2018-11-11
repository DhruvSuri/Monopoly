#! /usr/bin/env python
import Constant as constant

class Board:
		
	def __init__(self):
		print('Init of Board')
		self.board = {}
		self.board[constant.IN_JAIL_INDEX] = {}
		for i in range(constant.BOARD_SIZE):
			self.board[i] = {}