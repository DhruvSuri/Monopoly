#! /usr/bin/env python
from Game import Game
from Player import Player
import json

def main():
	print ('Playing Monopoly!')
	game = Game([Player(1), Player(2)])
	game.run()

if __name__ == '__main__':
	main()