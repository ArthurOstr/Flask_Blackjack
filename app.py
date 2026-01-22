from flask import Flask, render_template
from BJ_classes import Deck, Hand, Card

app = Flask(__name__)


@app.route("/")
def home():
    return '<a href="/deal">Start Game</a>'


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
