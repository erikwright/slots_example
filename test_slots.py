import random

from unittest import mock

import pytest

import slots

def test_slot_machine(monkeypatch):
    sm = slots.SlotMachine()
    sm.adjust_reserves(1000)
    sm.insert_money(25)
    initial_reels = sm.reels()
    winnings = sm.play()
    assert sm.reels() != initial_reels
    sm.insert_money(25)
    returned = sm.return_money()
    assert returned == 25
    for i in range(10):
        sm.insert_money(25)
        winnings += sm.play()
    assert winnings + sm.reserves() == 1000 + 25 * 11

    random_choice = mock.Mock()
    random_choice.side_effect = [
        slots.SlotMachine.Symbol.BELL,
        slots.SlotMachine.Symbol.BELL,
        slots.SlotMachine.Symbol.BELL
    ]
    monkeypatch.setattr(random, 'choice', random_choice)
    sm.insert_money(25)
    assert sm.play() == 25 * 16

    random_choice.side_effect = [
        slots.SlotMachine.Symbol.BELL,
        slots.SlotMachine.Symbol.BELL,
        slots.SlotMachine.Symbol.HEARTS
    ]
    monkeypatch.setattr(random, 'choice', random_choice)
    sm.insert_money(25)
    assert sm.play() == 25

    with pytest.raises(Exception):
        play()

    with pytest.raises(Exception):
        adjust_reserves(-10000)

    with pytest.raises(Exception):
        sm.insert_money(10)

    with pytest.raises(Exception):
        sm.insert_money(25)
        sm.insert_money(25)
