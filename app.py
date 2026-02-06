import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session
from BJ_classes import Deck, Hand, Card
from database import db, User
from werkzeug.security import generate_password_hash,check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key= os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
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

# Decorator for login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Guard logic
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if nickname is takem
        if User.query.filter_by(username=username).first():
            return "Nickname take! Try another one."

        # Hash and save password
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_pw, money=1000)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            return f"Database Error: {e}"

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('home'))

        return "Invalid login data"

    return render_template('login.html')


@app.route("/")
@login_required
def home():
    #fetch the current userdata
    current_user = db.session.get(User, session['user_id'])
    return render_template('home.html', user=current_user)


@app.route("/hit")
@login_required
def hit():
    # Load and deserialize deck to create object for the webpage
    deck_data = session.get('deck')
    if deck_data is None:
        return redirect(url_for('deal'))
    deck = Deck()
    deck.cards = [Card(c['rank'], c['suit']) for c in deck_data]

    # Changing Player's hand
    player_hand = dict_to_hand(session.get('player_hand'))

    # Draw the card from the changed deck
    player_hand.add_card(deck.draw())

    # Setting the strict logic
    if player_hand.get_value() > 21:
        session['result'] = "Bust! YOU GAINED MORE THAN 21"
        session['game_over'] = True

    # Memory of the game session
    session['deck'] = [{'rank': c.rank, 'suit': c.suit} for c in deck.cards]
    session['player_hand'] = object_to_dict(player_hand)

    return redirect(url_for('game_board'))


@app.route("/deal", methods=['POST'])
@login_required
def deal():
    # Get the user and the bet
    user = db.session.get(User, session['user_id'])
    bet_amount = int(request.form.get('bet_amount'))
    # Can the user afford bet?
    if user.money < bet_amount:
        return "You don't have enough money"
    user.money -= bet_amount
    db.session.commit()
    # Save bet session
    session['bet'] = bet_amount
    # initialize the game object
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


@app.route("/stand")
@login_required
def stand():
    # RESTORE THE STATE
    deck_data = session.get('deck')
    if deck_data is None:
        return redirect(url_for('deal'))
    player_data = session.get('player_hand')
    dealer_data = session.get('dealer_hand')
    
    deck = Deck()
    deck.cards = [Card(c['rank'], c['suit']) for c in deck_data]
    player_hand = dict_to_hand(player_data)
    dealer_hand = dict_to_hand(dealer_data)
    user = db.session.get(User, session['user_id'])
    bet = session.get('bet', 0)
    # THE DEALER'S TURN
    while dealer_hand.get_value() < 17:
        dealer_hand.add_card(deck.draw())
    # DETERMINE THE WINNER
    player_score = player_hand.get_value()
    dealer_score = dealer_hand.get_value()
    bet = session.get('bet', 0)
    user = User.query.get(session['user_id'])
    if dealer_score > 21:
        session['result'] = "Dealer busts, Player win!"
        user.money += bet * 2
    elif dealer_score > player_score:
        session['result'] = "Dealer win"
    elif dealer_score < player_score:
        session['result'] = "Player wins"
        user.money += bet * 2
    else:
        session['result'] = "It's a tie"

    db.session.commit()
    session['game_over'] = True
    # SAVE AND SHOW RESULTS
    session['deck'] = [{'rank':c.rank, 'suit':c.suit} for c in deck.cards]
    session['dealer_hand'] = object_to_dict(dealer_hand) 
    return redirect(url_for('game_board'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route("/game")
@login_required
def game_board():
    user = db.session.get(User, session['user_id'])
    player_data = session.get('player_hand')
    dealer_data = session.get('dealer_hand')
    result = session.get('result')
    game_over = session.get('game_over')

    if player_data is None:
        return redirect(url_for('home'))
    player_hand = dict_to_hand(player_data)
    dealer_hand = dict_to_hand(dealer_data)

    return render_template('game.html',
                           username=session.get('username'),
                           user=user,
                           player_hand=player_hand.hand,
                           player_score=player_hand.get_value(),
                           dealer_hand=dealer_data,
                           dealer_score=dealer_hand.get_value(),
                           result=session.get('result'),
                           game_over=session.get('game_over'))

if __name__ == "__main__":
    app.run(debug=True)
