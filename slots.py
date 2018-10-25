import collections
import enum
import json
import os
import random
import sys
import typing


class SlotException(Exception):
    pass


class Symbol(enum.Enum):
    HORSESHOES = 'Horseshoes'
    DIAMONDS = 'Diamonds'
    SPADES = 'Spades'
    HEARTS = 'Hearts'
    BELL = 'Bell'


class Configuration(typing.NamedTuple):
    reels: int = 3
    minimum_play: int = 25
    weights: typing.Tuple[typing.Tuple[Symbol, int], ...] = (
        (Symbol.HORSESHOES, 10),
        (Symbol.DIAMONDS, 5),
        (Symbol.SPADES, 5),
        (Symbol.HEARTS, 3),
        (Symbol.BELL, 1)
    )
    pay_table: typing.Tuple[typing.Tuple[str, int], ...] = (
        ('* *', 1),
        ('* * *', 2),
        ('Diamonds Spades Hearts', 4),
        ('Hearts Hearts Hearts', 8),
        ('Bell Bell Bell', 16)
    )



class SlotMachine:

    def __init__(self, configuration=Configuration()):
        self.__deposited = 0
        self.__prize_reserves = 0
        self.__minimum_play = configuration.minimum_play
        self.__reels = [Symbol.BELL for _ in range(configuration.reels)]
        self.__pay_table = dict(configuration.pay_table)
        self.__weights = dict(configuration.weights)

    def insert_money(self, amount):
        if self.__deposited:
            raise SlotException('Money already deposited.')
        if amount < self.__minimum_play:
            raise SlotException(f'The amount {amount} is below the minimum play {self.__minimum_play}.')
        self.__deposited = amount

    def return_money(self):
        (to_return, self.__deposited) = (self.__deposited, 0)
        return to_return

    def adjust_reserves(self, amount):
        if self.__prize_reserves + amount < 0:
            raise SlotException('Cannot withdraw more than reserve.')
        self.__prize_reserves += amount

    def reserves(self):
        return self.__prize_reserves

    def reels(self):
        return list(self.__reels)

    def play(self):
        if not self.__deposited:
            raise SlotException('Insert money prior to playing.')
        if self.__deposited * max(self.__pay_table.values()) > self.__prize_reserves:
            raise SlotException('Insufficient reserves for maximum possible payout.')

        self.__reels = self._spin()

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

    def _spin(self):
        return random.choices(
            list(Symbol),
            [self.__weights[symbol] for symbol in list(Symbol)],
            k=len(self.__reels)
        )


def load_configuration(path):
    configuration_dict = json.load(open(path))
    configuration = Configuration()
    if 'reels' in configuration_dict:
        configuration = configuration._replace(reels=configuration_dict['reels'])
    if 'pay_table' in configuration_dict:
        configuration = configuration._replace(pay_table=tuple(configuration_dict['pay_table'].items()))
    if 'weights' in configuration_dict:
        configuration = configuration._replace(weights=tuple(
            (Symbol(symbol), rate) for (symbol, rate) in configuration_dict['weights'].items()
        ))
    if 'minimum_play' in configuration_dict:
        configuration = configuration._replace(minimum_play=configuration_dict['minimum_play'])
    return configuration


def main():
    configuration = Configuration()
    cfg_path = os.environ.get('SLOTS_CFG_PATH', '.slots.cfg')
    if os.path.exists(cfg_path):
        configuration = load_configuration(cfg_path)
    slot_machine = SlotMachine(configuration)
    slot_machine.adjust_reserves(10000)
    while True:
        bet_string = input('Place your bet: ')
        try:
            bet = int(bet_string)
        except ValueError:
            print('Your bet must be a number!')
            continue
        slot_machine.insert_money(bet)
        winnings = slot_machine.play()
        print(' '.join(symbol.value for symbol in slot_machine.reels()))
        if winnings:
            print(f'You won {winnings}!')
        print('')


if __name__ == "__main__":
    main()
