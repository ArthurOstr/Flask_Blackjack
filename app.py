from flask import Flask, render_template, request, redirect, url_for, session
from BJ_classes import Deck, Hand, Card

app = Flask(__name__)


@app.route("/")
def home():
    return '<a href="/deal">Start Game</a>'


@app.route("/hit")
def hit():
    # Load and deserialize deck to create object for the webpage
    deck_data = session.get('deck')
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

    # send two objects to the HTML
    return render_template("game.html",
                           player_hand=player_hand.hand,
                           player_scoer=player_hand.get_value(),
                           dealer_hand=dealer_hand.hand)


if __name__ == "__main__":
    app.run(debug=True)
