#! /usr/bin/env python
import Constant as constant
from logger import logger
from Dice import Dice
from Board import Board

class Game:

	def move(self, player, dice_roll):
		logger.info("Player making move!!");

	def __init__(self, players):
		self.board = Board()

		self.players = players

		# Dice initialization
		self.dices = []
		for seed in constant.DICE_SEEDS:
			self.dices.append(Dice(seed))
		
		# Initial Position of the players at the start of the game.
		self.position = [(0,0)]

		# By default first player will play the game
		self.turn = 0

		# State History
		self.state_hist = []

	def run(self):
		logger.info("Game started!")

		for move_count in range(constant.MAX_MOVES):
			logger.info("Move: " + str(move_count + 1))
			logger.info("Player %d turn", self.turn+1)

			# Die Roll
			rolls = [];
			for dice in self.dices:
				rolls.append(dice.roll());
			dice_roll = tuple(rolls)
			logger.info("Dice Roll:" + str(dice_roll))

			# Make a move
			self.move(self.players[self.turn], dice_roll)

			state = dict()
			state['dice_roll'] = dice_roll 
			self.state_hist.append(state);

			self.turn = (self.turn + 1) % constant.MAX_PLAYERS