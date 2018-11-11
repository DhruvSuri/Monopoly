#! /usr/bin/env python
import Constant as constant
import numpy as np

class Dice:

    def __init__(self, state):
        self.rnd = np.random.RandomState(state)

    def roll(self):
        return self.rnd.randint(constant.DICE_ROLL_MIN, constant.DICE_ROLL_MAX)
