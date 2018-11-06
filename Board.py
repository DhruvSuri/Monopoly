#! /usr/bin/env python
import constant

'''
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

'''

#TODO: Should be singleton
class Board:
		
	def __init__(self):
		print ('Init of Board')
		self.board = {}
		self.board[constant.IN_JAIL_INDEX] = {}
		for i in range(constant.BOARD_SIZE):
			self.board[i] = {}