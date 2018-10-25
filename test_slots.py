import pytest

import slots

def test_slot_machine():
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
