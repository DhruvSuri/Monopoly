#! /usr/bin/env python
import logging

class Player:
	def __init__(self):
		logger = logging.getLogger("com.sbu.monopoly.player")
		logger.info("Player initialized")