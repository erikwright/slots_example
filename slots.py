import collections
import enum
import json
import os
import random

class SlotMachine:

    class Symbol(enum.Enum):
        HORSESHOES = 'Horshoes'
        DIAMONDS = 'Diamonds'
        SPADES = 'Spades'
        HEARTS = 'Hearts'
        BELL = 'Bell'

    def __init__(self):
        self.__deposited = 0
        self.__prize_reserves = 0
        self.__reels = [self.Symbol.BELL for _ in range(3)]

    def insert_money(self, amount):
        self.__deposited = amount

    def return_money(self):
        (to_return, self.__deposited) = (self.__deposited, 0)
        return to_return

    def adjust_reserves(self, amount):
        self.__prize_reserves += amount

    def reserves(self):
        return self.__prize_reserves

    def reels(self):
        return list(self.__reels)

    def play(self):
        for i in range(len(self.__reels)):
            self.__reels[i] = random.choice(list(self.Symbol))
        winnings = 0
        self.__prize_reserves += self.__deposited - winnings
        self.__deposited = 0

        return winnings
