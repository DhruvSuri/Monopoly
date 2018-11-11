#! /usr/bin/env python
import logging

class Player:
	def __init__(self):
		logger = logging.getLogger("com.sbu.monopoly.player")
		logger.info("Player initialized")

	def getBMSTDecision(self, state):
		return action	

	def respondTrade(self, state):
		return action
	
	def buyProperty(self, state):
		return True
	
	def auctionProperty(self, state):
		return False
	
	def respondMortgage(self, state):
		return True

	def jailDecision(self, state):
		return ("P")
	
	