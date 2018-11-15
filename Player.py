#! /usr/bin/env python
import logging

class Player:
	def __init__(self, id):
		self.logger = logging.getLogger("com.sbu.monopoly.player")
		self.id = id
		self.state = None
		self.logger.info("Player %d initialized", self.id)

	def getBMSTDecision(self, state):
		return None

	def respondTrade(self, state):
		return None
	
	def buyProperty(self, state):
		return True
	
	def auctionProperty(self, state):
		return False
	
	def receiveState(self, state):
		self.state = state
		self.logger.info("Player %d received new state", self.id)
		
	def respondMortgage(self, state):
		return True

	def jailDecision(self, state):
		# ToDo: Different actions needs to be modelled R, P or C
		# Currently in greedy approach modelling as P
		return ("P")
	
	