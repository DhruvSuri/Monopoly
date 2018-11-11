#! /usr/bin/env python
import Constant as constant
from logger import logger
from Dice import Dice
from Board import Board
from State import State
from copy import deepcopy

class Game:
	def __init__(self, players):
		# Board initialization
		self.board = Board()

		self.players = players

		# Dice initialization
		self.dices = []
		for seed in constant.DICE_SEEDS:
			self.dices.append(Dice(seed))

		# Current State
		property_status_arr = [0 for x in range(constant.PROPERTY_COUNT)]
		self.cur_state = State(constant.TURN_INIT, constant.INITIAL_DICE_ROLL, \
		constant.INITIAL_POSITION, constant.INITIAL_CASH_HOLDINGS, constant.BANK_MONEY, property_status_arr)

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
			self.turn_player_id = turn_player_id

			# Make a move
			self.runPlayerOnState(self.players[turn_player_id], self.cur_state, self.state_hist)

			# Storing in state_hist
			self.state_hist.append(deepcopy(self.cur_state))
		logger.info("Property Status: %s", str(self.cur_state.property_status))

	def runPlayerOnState(self, player, cur_state, state_hist):
		# curr_state - property_status

		#based on BSMT decision
		self.handle_buy(player, cur_state)

		logger.info("Player making move!!");

	def handle_buy(self, player, curr_state):
		property_status = curr_state.property_status
		player_id = self.turn_player_id
		position = curr_state.position[player_id]
		cash_holding = curr_state.cash_holdings[player_id]
		property_json = self.board.board_config[str(position)]

		if(curr_state.property_status[position] == 0 and property_json["rent_hotel"] > 0):
			curr_state.property_status[position] = self.get_property_status(player_id)
			logger.info("Property %s purchased by Player: %s", str(property_json["name"]), str(player_id))

	def get_property_status(self, turn_player_id):
		#Define the complete enum for buying property and house
		if (turn_player_id == 0):
			return 1
		else: 
			return -1

















		

