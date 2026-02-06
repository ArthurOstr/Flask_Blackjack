import pytest
from BJ_classes import Card, Hand

def test_basic_hand_value():
    hand = Hand()
    hand.add_card(Card('King', 'Spades'))
    hand.add_card(Card('5', 'Hearts'))

    assert hand.get_value() == 15

def test_ace_as_eleven():
    hand = Hand()
    hand.add_card(Card('Ace', 'Diamonds'))
    hand.add_card(Card('9', 'Clubs'))
    hand.add_card(Card('5', 'Spades'))

    assert hand.get_value() == 15
