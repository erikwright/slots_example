import collections
from unittest import mock

import pytest

import slots

def test_slot_machine(monkeypatch, tmpdir):
    sm = slots.SlotMachine()
    sm.adjust_reserves(1000)
    sm.insert_money(25)
    returned = sm.return_money()
    assert returned == 25

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

    with pytest.raises(Exception):
        play()

    with pytest.raises(Exception):
        adjust_reserves(-10000)

    with pytest.raises(Exception):
        sm.insert_money(10)

    with pytest.raises(Exception):
        sm.insert_money(25)
        sm.insert_money(25)

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

    config_file = tmpdir.join('.slots.cfg')
    monkeypatch.setenv('SLOTS_CFG_PATH', str(config_file))
    sm = slots.SlotMachine()
    with pytest.raises(Exception):
        sm.insert_money(15)

    config_file.write('''
{
    "minimum_play": 15,
    "reels": 5,
    "pay_table": {
        "Horseshoes Horseshoes Horseshoes Horseshoes Horseshoes": 32,
        "* * * * *": 16
    },
    "weights": {
        "Horseshoes": 5,
        "Diamonds": 4,
        "Spades": 3,
        "Hearts": 2,
        "Bell": 1
    }
}
''')
    sm = slots.SlotMachine()
    sm.insert_money(15)


    counter = collections.Counter()
    for i in range(100000):
        sm = slots.SlotMachine()
        sm.adjust_reserves(1000)
        sm.insert_money(25)
        sm.play()
        counter.update(sm.reels())

    def assert_approx(expected, actual):
        assert abs(actual - expected) < expected * 0.05

    assert sum(counter[symbol] for symbol in list(slots.SlotMachine.Symbol)) == 500000
    assert_approx(expected=counter[slots.SlotMachine.Symbol.BELL] * 5,
                  actual=counter[slots.SlotMachine.Symbol.HORSESHOES])
    assert_approx(expected=counter[slots.SlotMachine.Symbol.BELL] * 4,
                  actual=counter[slots.SlotMachine.Symbol.DIAMONDS])
    assert_approx(expected=counter[slots.SlotMachine.Symbol.BELL] * 3,
                  actual=counter[slots.SlotMachine.Symbol.SPADES])
    assert_approx(expected=counter[slots.SlotMachine.Symbol.BELL] * 2,
                  actual=counter[slots.SlotMachine.Symbol.HEARTS])
