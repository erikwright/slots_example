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
        slots.SlotMachine.Symbol.BELL,
        slots.SlotMachine.Symbol.BELL,
        slots.SlotMachine.Symbol.BELL
    ]]
    sm.insert_money(25)
    assert sm.play() == 25 * 16
    assert sm.reels() == [
        slots.SlotMachine.Symbol.BELL,
        slots.SlotMachine.Symbol.BELL,
        slots.SlotMachine.Symbol.BELL
    ]

    spin.side_effect = [[
        slots.SlotMachine.Symbol.BELL,
        slots.SlotMachine.Symbol.BELL,
        slots.SlotMachine.Symbol.HEARTS
    ]]
    sm.insert_money(25)
    assert sm.play() == 25
    assert sm.reels() == [
        slots.SlotMachine.Symbol.BELL,
        slots.SlotMachine.Symbol.BELL,
        slots.SlotMachine.Symbol.HEARTS
    ]


def test_raise_play_without_money():
    def play(with_money):
        sm = slots.SlotMachine()
        sm.adjust_reserves(1000)
        if with_money:
            sm.insert_money(25)
        sm.play()

    play(with_money=True)
    with pytest.raises(Exception):
        play(with_money=False)


def test_raise_excessive_withdrawal():
    def withdraw(amount):
        sm = slots.SlotMachine()
        sm.adjust_reserves(1000)
        sm.adjust_reserves(-amount)

    withdraw(500)
    withdraw(1000)
    with pytest.raises(Exception):
        withdraw(1001)


def test_raise_below_minimum_play():
    def insert_money(amount):
        sm = slots.SlotMachine()
        sm.insert_money(amount)

    insert_money(25)
    with pytest.raises(Exception):
        insert_money(10)


def test_raise_double_insert():
    sm = slots.SlotMachine()
    sm.adjust_reserves(1000)
    sm.insert_money(25)
    with pytest.raises(Exception):
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

    assert sum(counter[symbol] for symbol in list(slots.SlotMachine.Symbol)) == 300000
    assert_approx(expected=counter[slots.SlotMachine.Symbol.BELL] * 10,
                  actual=counter[slots.SlotMachine.Symbol.HORSESHOES])
    assert_approx(expected=counter[slots.SlotMachine.Symbol.BELL] * 5,
                  actual=counter[slots.SlotMachine.Symbol.DIAMONDS])
    assert_approx(expected=counter[slots.SlotMachine.Symbol.BELL] * 5,
                  actual=counter[slots.SlotMachine.Symbol.SPADES])
    assert_approx(expected=counter[slots.SlotMachine.Symbol.BELL] * 3,
                  actual=counter[slots.SlotMachine.Symbol.HEARTS])


def test_config_file_is_missing(monkeypatch, tmpdir):
    config_file = tmpdir.join('.slots.cfg')
    monkeypatch.setenv('SLOTS_CFG_PATH', str(config_file))
    sm = slots.SlotMachine()
    sm.adjust_reserves(1000)
    with pytest.raises(Exception):
        sm.insert_money(15)
    sm.insert_money(25)


def test_config_minimum_play(monkeypatch, tmpdir):
    config_file = tmpdir.join('.slots.cfg')
    monkeypatch.setenv('SLOTS_CFG_PATH', str(config_file))
    config_file.write('{"minimum_play": 15}')
    sm = slots.SlotMachine()
    sm.insert_money(15)


def test_config_reels(monkeypatch, tmpdir):
    config_file = tmpdir.join('.slots.cfg')
    monkeypatch.setenv('SLOTS_CFG_PATH', str(config_file))
    config_file.write('{"reels": 5}')
    sm = slots.SlotMachine()
    assert len(sm.reels()) == 5
    sm.adjust_reserves(1000)
    sm.insert_money(25)
    sm.play()
    assert len(sm.reels()) == 5


def test_config_weights(monkeypatch, tmpdir):
    config_file = tmpdir.join('.slots.cfg')
    monkeypatch.setenv('SLOTS_CFG_PATH', str(config_file))

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

    counter = collections.Counter()
    for i in range(100000):
        sm = slots.SlotMachine()
        sm.adjust_reserves(1000)
        sm.insert_money(25)
        sm.play()
        counter.update(sm.reels())

    def assert_approx(expected, actual):
        assert abs(actual - expected) < expected * 0.05

    assert sum(counter[symbol] for symbol in list(slots.SlotMachine.Symbol)) == 300000
    assert_approx(expected=counter[slots.SlotMachine.Symbol.BELL] * 5,
                  actual=counter[slots.SlotMachine.Symbol.HORSESHOES])
    assert_approx(expected=counter[slots.SlotMachine.Symbol.BELL] * 4,
                  actual=counter[slots.SlotMachine.Symbol.DIAMONDS])
    assert_approx(expected=counter[slots.SlotMachine.Symbol.BELL] * 3,
                  actual=counter[slots.SlotMachine.Symbol.SPADES])
    assert_approx(expected=counter[slots.SlotMachine.Symbol.BELL] * 2,
                  actual=counter[slots.SlotMachine.Symbol.HEARTS])


def test_config_pay_table(monkeypatch, tmpdir):
    config_file = tmpdir.join('.slots.cfg')
    monkeypatch.setenv('SLOTS_CFG_PATH', str(config_file))

    config_file.write('''{
    "pay_table": {
        "Horseshoes Horseshoes Horseshoes": 10
    }
}
''')

    sm = slots.SlotMachine()
    sm.adjust_reserves(1000)
    spin = mock.Mock()
    monkeypatch.setattr(sm, '_spin', spin)

    spin.side_effect = [[
        slots.SlotMachine.Symbol.HORSESHOES,
        slots.SlotMachine.Symbol.HORSESHOES,
        slots.SlotMachine.Symbol.HORSESHOES
    ]]
    sm.insert_money(25)
    assert sm.play() == 25 * 10
