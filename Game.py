#! /usr/bin/env python
import constant
from Board import Board
from Player import Player


#TODO: Should be singleton
class Game:

	def move(self, player):
		assert isinstance(player, Player), 'argument of move should of Player type'
		print ('In move')


	def __init__(self):
		print ('Init of Game')
		self.board = Board()
		self.players = [Player(),Player()]
		self.position = [[0,0], [0,0]]
		self.move(self.players[0])



