#! /usr/bin/env python

# Game configuration
MAX_MOVES = 100
BANK_MONEY = 5000

# Board Configuration
BOARD_SIZE = 40
IN_JAIL_INDEX = -1

# Dice Configuration
DICE_ROLL_MAX_VALUE = 6
DICE_ROLL_MIN_VALUE = 1
DICE_SEEDS = [101, 997]
INITIAL_DICE_ROLL = [(0, 0)]
MAX_ROLLS_FOR_JAIL = 3

# Players Configuration
MAX_PLAYERS = 2
INITIAL_POSITION = (0, 0)
INITIAL_CASH_HOLDINGS = (1500, 1500)

# Turn
TURN_INIT = -1

# Property status
INITIAL_PROPERTY_STATUS = 0
PROPERTY_COUNT = 42

#Chance and Community Card
CHANCE_CARD_FILE_NAME = 'ChanceCards.json'
COMMUNITY_CARDS_FILE_NAME = 'CommunityChestCards.json'
MAX_CHANCE_CARD = 16
MAX_COMMUNITY_CARD = 16
