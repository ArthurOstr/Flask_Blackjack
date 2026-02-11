import random

class Deck:
    def __init__(self):
        self.restart()

#taking 1 card from the deck
    def draw(self):
        card = random.choice(self.cards)
        self.cards.remove(card)
        return card

#It seems I can look at cards in my deck
    def look_deck(self):
        return len(self.cards)

#reshuffle the deck when needed
    def restart(self):
        suits = ["Clubs", "Diamonds", "Hearts", "Spades"]
        ranks = ["Jack", "Queen", "King", "Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        self.cards = [Card(rank, suit) for rank in ranks for suit in suits]



class Card:
    def __init__(self, rank, suit, visible=True):
        self.rank = rank
        self.suit = suit
        self.visible = visible

#how does card looks like
    def show(self):
        if not self.visible:
            return "Hidden Card"
        else:
            return f"{self.rank} of {self.suit}"

    def flip(self):
        self.visible = not self.visible


class Hand:
    def __init__(self):
        self.hand = []
        self.stored_cards = []

    def __len__(self):
        return len(self.hand)

#adding card to my hand
    def add_card(self, card):
        self.hand.append(card)

    def restart_hand(self):
        self.hand = []

    def remove_card(self):
        if not self.hand:
            print("Hand is empty, cannot remove card.")
            return

        removed_card = self.hand.pop(0)
        self.stored_cards.append(removed_card)

        print (f"Success removing {removed_card.show()} from hand.")

    def show_hand(self):
        return [card.show() for card in self.hand]

    def multiple_flip(self):
        for card in self.hand:
            if not card.visible:
                card.flip()

    def get_value(self):
        value = 0
        aces = 0
        for card in self.hand:
            if card.rank in ['Jack', 'Queen', 'King']:
                value += 10
            elif card.rank == 'Ace':
                aces += 1
                value += 11
            else:
                value += int(card.rank)
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

#It seems I can look at cards in my hand
    def look(self):
        return len(self.hand)

class Dealer:
    def __init__(self,deck):
        self.deck = deck
        self.hand = Hand()

    def deal_card(self,visible=True):
        card = self.deck.draw()
        card.visible = visible
        self.hand.add_card(card)

    def restart(self):
        self.hand = Hand()
        print("Dealer's hand is empty")

    def reveal(self):
        self.hand.multiple_flip()
        print("Dealer revealed his cards")

class Player:

    def __init__(self, balance=1000, win_count=0):
        self.hand = Hand()
        self.balance = balance
        self.current_bet = 0
        self.win_count = win_count

    def receive_card(self, card):
        self.hand.add_card(card)

    def place_bet(self, amount):
        if amount > self.balance:
            print("Bet exceeds available balance")
            return
        self.current_bet = amount
        self.balance -= amount

    def win_bet(self):
        self.balance += 2 * self.current_bet
        self.win_count += 1
        print(f"Player wins {self.current_bet * 2}!")

    def lose_bet(self):
        print(f"Player loses {self.current_bet}!")

    def push_bet(self):
        self.balance += self.current_bet
        print("It's a push! Bet returned to player.")

    #way to double bet
    def double_bet(self, deck):
        if self.balance >= self.current_bet:
            self.current_bet *= 2
            self.receive_card(deck)
            return True
        elif self.balance <= self.current_bet:
            return False




