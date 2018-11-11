#! /usr/bin/env python
import Constant as constant
from logger import logger
from Dice import Dice
from Board import Board
from State import State
from copy import deepcopy

class Game:

	def move(self, player, cur_state, state_hist):
		logger.info("Player making move!!");

	def __init__(self, players):
		# Board initialization
		self.board = Board()

		self.players = players

		# Dice initialization
		self.dices = []
		for seed in constant.DICE_SEEDS:
			self.dices.append(Dice(seed))

		# Current State
		self.cur_state = State(constant.TURN_INIT, constant.INITIAL_DICE_ROLL, \
		constant.INITIAL_POSITION, constant.INITIAL_CASH_HOLDINGS, constant.BANK_MONEY)

		# State History
		self.state_hist = []

	def run(self):
		logger.info("Game started!")

		for move_count in range(constant.MAX_MOVES):
			logger.info("Move: " + str(move_count + 1))

			# Turn calculation
			turn = self.cur_state.turn + 1
			turn_player_id = (turn % constant.MAX_PLAYERS)
			logger.info("Player %d turn", turn_player_id)

			# Dice Roll
			rolls = []
			for dice in self.dices:
				rolls.append(dice.roll())
			dice_roll = tuple(rolls)
			logger.info("Dice Roll: %s", str(dice_roll))

			# Calculating new position
			position_list = list(self.cur_state.position)
			position_list[turn_player_id] = (position_list[turn_player_id] + dice_roll[0] + dice_roll[1]) % self.board.total_board_cells
			position = tuple(position_list)
			logger.info("New position: %s", str(position))
			
			# Forming new current state
			self.cur_state.turn = turn
			self.cur_state.dice_roll = dice_roll
			self.cur_state.position = position

			# Make a move
			self.move(self.players[turn_player_id], self.cur_state, self.state_hist)

			# Storing in state_hist
			self.state_hist.append(deepcopy(self.cur_state))