#! /usr/bin/env python
import logging

class Player:
	def __init__(self, id):
		logger = logging.getLogger("com.sbu.monopoly.player")
		self.id = id
		self.state = None
		logger.info("Player %d initialized", self.id)

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
		
	def respondMortgage(self, state):
		return True

	def jailDecision(self, state):
		# ToDo: Different actions needs to be modelled R, P or C
		# Currently in greedy approach modelling as P
		return ("P")
	
	