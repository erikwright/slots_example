import collections
from unittest import mock

import pytest

import slots


def test_return_money():
    sm = slots.SlotMachine()
    sm.adjust_reserves(1000)
    sm.insert_money(25)
    returned = sm.return_money()
    assert returned == 25


def test_pay_table(monkeypatch):
    sm = slots.SlotMachine()
    sm.adjust_reserves(1000)
    spin = mock.Mock()
    monkeypatch.setattr(sm, '_spin', spin)

    spin.side_effect = [[
        slots.Symbol.BELL,
        slots.Symbol.BELL,
        slots.Symbol.BELL
    ]]
    sm.insert_money(25)
    assert sm.play() == 25 * 16
    assert sm.reels() == [
        slots.Symbol.BELL,
        slots.Symbol.BELL,
        slots.Symbol.BELL
    ]

    spin.side_effect = [[
        slots.Symbol.BELL,
        slots.Symbol.BELL,
        slots.Symbol.HEARTS
    ]]
    sm.insert_money(25)
    assert sm.play() == 25
    assert sm.reels() == [
        slots.Symbol.BELL,
        slots.Symbol.BELL,
        slots.Symbol.HEARTS
    ]


def test_raise_play_without_money():
    def play(with_money):
        sm = slots.SlotMachine()
        sm.adjust_reserves(1000)
        if with_money:
            sm.insert_money(25)
        sm.play()

    play(with_money=True)
    with pytest.raises(slots.SlotException):
        play(with_money=False)


def test_raise_excessive_withdrawal():
    def withdraw(amount):
        sm = slots.SlotMachine()
        sm.adjust_reserves(1000)
        sm.adjust_reserves(-amount)

    withdraw(500)
    withdraw(1000)
    with pytest.raises(slots.SlotException):
        withdraw(1001)


def test_raise_below_minimum_play():
    def insert_money(amount):
        sm = slots.SlotMachine()
        sm.insert_money(amount)

    insert_money(25)
    with pytest.raises(slots.SlotException):
        insert_money(10)


def test_raise_double_insert():
    sm = slots.SlotMachine()
    sm.adjust_reserves(1000)
    sm.insert_money(25)
    with pytest.raises(slots.SlotException):
        sm.insert_money(25)


def test_weighted_spinning():
    counter = collections.Counter()
    for i in range(100000):
        sm = slots.SlotMachine()
        sm.adjust_reserves(1000)
        sm.insert_money(25)
        sm.play()
        counter.update(sm.reels())

    def assert_approx(expected, actual):
        assert abs(actual - expected) < expected * 0.05

    assert sum(counter[symbol] for symbol in list(slots.Symbol)) == 300000
    assert_approx(expected=counter[slots.Symbol.BELL] * 10,
                  actual=counter[slots.Symbol.HORSESHOES])
    assert_approx(expected=counter[slots.Symbol.BELL] * 5,
                  actual=counter[slots.Symbol.DIAMONDS])
    assert_approx(expected=counter[slots.Symbol.BELL] * 5,
                  actual=counter[slots.Symbol.SPADES])
    assert_approx(expected=counter[slots.Symbol.BELL] * 3,
                  actual=counter[slots.Symbol.HEARTS])


def test_config_file_is_missing(monkeypatch, tmpdir):
    config_file = tmpdir.join('.slots.cfg')
    monkeypatch.setenv('SLOTS_CFG_PATH', str(config_file))
    sm = slots.SlotMachine()
    sm.adjust_reserves(1000)
    with pytest.raises(slots.SlotException):
        sm.insert_money(15)
    sm.insert_money(25)


def test_config_minimum_play():
    def insert_fifteen(configuration):
        slots.SlotMachine(configuration).insert_money(15)

    with pytest.raises(slots.SlotException):
        insert_fifteen(slots.Configuration())
    insert_fifteen(slots.Configuration(minimum_play=15))


def test_load_configuration_minimum_play(tmpdir):
    config_file = tmpdir.join('.slots.cfg')
    config_file.write('{"minimum_play": 15}')
    assert slots.load_configuration(str(config_file)) == slots.Configuration(minimum_play=15)


def test_config_reels(tmpdir):
    default_reels = slots.SlotMachine(slots.Configuration())
    five_reels = slots.SlotMachine(slots.Configuration(reels=5))
    assert len(default_reels.reels()) == 3
    assert len(five_reels.reels()) == 5

    five_reels.adjust_reserves(1000)
    five_reels.insert_money(25)
    five_reels.play()
    assert len(five_reels.reels()) == 5


def test_load_configuration_reels(tmpdir):
    config_file = tmpdir.join('.slots.cfg')
    config_file.write('{"reels": 5}')
    assert slots.load_configuration(str(config_file)) == slots.Configuration(reels=5)


def test_config_weights():
    configuration = slots.Configuration(
        weights=(
            (slots.Symbol.HORSESHOES, 5),
            (slots.Symbol.DIAMONDS, 4),
            (slots.Symbol.SPADES, 3),
            (slots.Symbol.HEARTS, 2),
            (slots.Symbol.BELL, 1)
        )
    )
    counter = collections.Counter()
    for i in range(100000):
        sm = slots.SlotMachine(configuration)
        sm.adjust_reserves(1000)
        sm.insert_money(25)
        sm.play()
        counter.update(sm.reels())

    def assert_approx(expected, actual):
        assert abs(actual - expected) < expected * 0.05

    assert sum(counter[symbol] for symbol in list(slots.Symbol)) == 300000
    assert_approx(expected=counter[slots.Symbol.BELL] * 5,
                  actual=counter[slots.Symbol.HORSESHOES])
    assert_approx(expected=counter[slots.Symbol.BELL] * 4,
                  actual=counter[slots.Symbol.DIAMONDS])
    assert_approx(expected=counter[slots.Symbol.BELL] * 3,
                  actual=counter[slots.Symbol.SPADES])
    assert_approx(expected=counter[slots.Symbol.BELL] * 2,
                  actual=counter[slots.Symbol.HEARTS])


def test_load_configuration_weights(tmpdir):
    config_file = tmpdir.join('.slots.cfg')
    config_file.write('''{
    "weights": {
        "Horseshoes": 5,
        "Diamonds": 4,
        "Spades": 3,
        "Hearts": 2,
        "Bell": 1
    }
}
''')
    assert slots.load_configuration(str(config_file)) == slots.Configuration(
        weights=(
            (slots.Symbol.HORSESHOES, 5),
            (slots.Symbol.DIAMONDS, 4),
            (slots.Symbol.SPADES, 3),
            (slots.Symbol.HEARTS, 2),
            (slots.Symbol.BELL, 1)
        )
    )


def test_config_pay_table(monkeypatch):
    sm = slots.SlotMachine(slots.Configuration(
        pay_table=(
            ("Horseshoes Horseshoes Horseshoes", 10),
        )
    ))
    sm.adjust_reserves(1000)
    spin = mock.Mock()
    monkeypatch.setattr(sm, '_spin', spin)

    spin.side_effect = [[
        slots.Symbol.HORSESHOES,
        slots.Symbol.HORSESHOES,
        slots.Symbol.HORSESHOES
    ]]
    sm.insert_money(25)
    assert sm.play() == 25 * 10


def test_load_configuration_pay_table(tmpdir):
    config_file = tmpdir.join('.slots.cfg')
    config_file.write('''{
    "pay_table": {
        "Horseshoes Horseshoes Horseshoes": 10
    }
}
''')

    assert slots.load_configuration(str(config_file)) == slots.Configuration(
        pay_table=(
            ("Horseshoes Horseshoes Horseshoes", 10),
        )
    )
