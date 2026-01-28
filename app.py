from flask import Flask, render_template, request, redirect, url_for, session
from BJ_classes import Deck, Hand, Card

app = Flask(__name__)
app.secret_key= "Arthur_Is_The_King"

# Helper functions
def object_to_dict(hand_object):
    card_list = []
    for card in hand_object.hand:
        card_list.append({'rank': card.rank, 'suit': card.suit})
    return card_list

def dict_to_hand(card_list):
    hand = Hand() 
    if card_list is None:
        return hand
    else:
        for card_data in card_list:
            recreated_card = Card(card_data['rank'], card_data['suit'])
            hand.add_card(recreated_card)
        return hand


@app.route("/")
def home():
    return '<a href="/deal">Start Game</a>'


@app.route("/hit")
def hit():
    # Load and deserialize deck to create object for the webpage
    deck_data = session.get('deck')
    if deck_data is None:
        return redirect(url_for('deal' ))
    deck = Deck()
    deck.cards = [Card(c['rank'], c['suit']) for c in deck_data]

    # Changing Player's hand
    player_hand = dict_to_hand(session.get('player_hand'))

    # Draw the card from the changed deck
    new_card = deck.draw()
    player_hand.add_card(new_card)

    # Setting the strict logic
    if player_hand.get_value() > 21:
        session['result'] = "Bust! YOU GAINED MORE THAN 21"
        session['game_over'] = True

    # Memory of the game session
    session['deck'] = [{'rank': c.rank, 'suit': c.suit} for c in deck.cards]
    session['player_hand'] = object_to_dict(player_hand)

    return redirect(url_for('game_board'))


@app.route("/deal")
def deal():
    # initialize the game objec
    deck = Deck()
    player_hand = Hand()
    dealer_hand = Hand()

    # deal 2 cards
    player_hand.add_card(deck.draw())
    player_hand.add_card(deck.draw())

    dealer_hand.add_card(deck.draw())
    dealer_hand.add_card(deck.draw())

    session['deck'] = [{'rank': c.rank, 'suit': c.suit} for c in deck.cards]
    session['player_hand'] = object_to_dict(player_hand)
    session['dealer_hand'] = object_to_dict(dealer_hand)
    session['result'] = None
    session['game_over'] = False

    return redirect(url_for('game_board'))

@app.route("/game")
def game_board():

    player_data = session.get('player_hand')
    dealer_data = session.get('dealer_hand')
    result = session.get('result')
    game_over = session.get('game_over')

    if player_data is None:
        return redirect(url_for('deal'))
    player_hand = dict_to_hand(player_data)

    return render_template('game.html',
                           player_hand=player_hand.hand,
                           player_score=player_hand.get_value(),
                           dealer_hand=dealer_data,
                           result=result,
                           game_over=game_over)

if __name__ == "__main__":
    app.run(debug=True)
