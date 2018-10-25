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
        cfg_path = os.environ.get('SLOTS_CFG_PATH', '.slots.cfg')
        self.__config = json.load(open(cfg_path)) if cfg_path and os.path.exists(cfg_path) else {}
        self.__deposited = 0
        self.__prize_reserves = 0
        self.__reels = [self.Symbol.BELL for _ in range(self.__config.get('reels', 3))]
        self.__pay_table = self.__config.get('pay_table', self.__DEFAULT_PAY_TABLE)

    def insert_money(self, amount):
        if self.__deposited:
            raise Exception('Money already deposited.')
        minimum_play = self.__config.get('minimum_play', 25)
        if amount < minimum_play:
            raise Exception(f'The amount {amount} is below the minimum play {minimum_play}.')
        self.__deposited = amount

    def return_money(self):
        (to_return, self.__deposited) = (self.__deposited, 0)
        return to_return

    def adjust_reserves(self, amount):
        if self.__prize_reserves + amount < 0:
            raise Exception('Cannot withdraw more than reserve.')
        self.__prize_reserves += amount

    def reserves(self):
        return self.__prize_reserves

    def reels(self):
        return list(self.__reels)

    def play(self):
        if not self.__deposited:
            raise Exception('Insert money prior to playing.')
        if self.__deposited * max(self.__pay_table.values()) > self.__prize_reserves:
            raise Exception('Insufficient reserves for maximum possible payout.')

        for i in range(len(self.__reels)):
            self.__reels[i] = random.choice(list(self.Symbol))
        pay_table_key = ' '.join(reel.value for reel in self.__reels)
        if pay_table_key not in self.__pay_table:
            counter = collections.Counter(self.__reels)
            highest_count = counter.most_common(1)[0][1]
            for i in reversed(range(highest_count)):
                pay_table_key = ' '.join('*' * (i + 1))
                if pay_table_key in self.__pay_table:
                    break
        winnings = self.__pay_table.get(pay_table_key, 0) * self.__deposited

        self.__prize_reserves += self.__deposited - winnings
        self.__deposited = 0

        return winnings

    __DEFAULT_PAY_TABLE = {
        '* *': 1,
        '* * *': 2,
        'Diamonds Spades Hearts': 4,
        'Hearts Hearts Hearts': 8,
        'Bell Bell Bell': 16
    }
