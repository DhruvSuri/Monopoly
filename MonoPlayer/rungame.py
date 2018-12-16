#! /usr/bin/env python
from Game import Game
from Player import Player
import json

def main():
	print ('Playing Monopoly!')
	game = Game()
	game.run([Player(1), Player(2)])

if __name__ == '__main__':
	main()