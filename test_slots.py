import random

from unittest import mock

import pytest

import slots

def test_slot_machine(monkeypatch):
    sm = slots.SlotMachine()
    sm.adjust_reserves(1000)
    sm.insert_money(25)
    returned = sm.return_money()
    assert returned == 25

    random_choice = mock.Mock()
    monkeypatch.setattr(random, 'choice', random_choice)

    random_choice.side_effect = [
        slots.SlotMachine.Symbol.BELL,
        slots.SlotMachine.Symbol.BELL,
        slots.SlotMachine.Symbol.BELL
    ]
    sm.insert_money(25)
    assert sm.play() == 25 * 16
    assert sm.reels() == [
        slots.SlotMachine.Symbol.BELL,
        slots.SlotMachine.Symbol.BELL,
        slots.SlotMachine.Symbol.BELL
    ]

    random_choice.side_effect = [
        slots.SlotMachine.Symbol.BELL,
        slots.SlotMachine.Symbol.BELL,
        slots.SlotMachine.Symbol.HEARTS
    ]
    monkeypatch.setattr(random, 'choice', random_choice)
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
