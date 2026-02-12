import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from BJ_classes import Deck, Hand, Card
from database import db, User, Game, init_db
from sqlalchemy.orm.attributes import flag_modified
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
if not app.config["SQLALCHEMY_DATABASE_URI"]:
    raise RuntimeError("DATABASE_URL is not set")

db.init_app(app)
with app.app_context():
    init_db(app)


# Helper functions
def object_to_dict(hand_object):
    card_list = []
    for card in hand_object.hand:
        card_list.append({"rank": card.rank, "suit": card.suit})
    return card_list


def dict_to_hand(card_list):
    hand = Hand()
    if card_list is None:
        return hand
    else:
        for card_data in card_list:
            recreated_card = Card(card_data["rank"], card_data["suit"])
            hand.add_card(recreated_card)
        return hand


# Decorator for login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Guard logic
        if "user_id" not in session:
            return jsonify({"error": "Authentication requiered"}), 401
        return f(*args, **kwargs)

    return decorated_function


@app.route("/api/user/profile")
def get_profile():
    # Get data from debug
    user_id = session.get("user_id")
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"Error": "No users found"}), 404
    return jsonify(
        {
            "username": user.username,
            "money": user.money,
            "wins": user.wins,
            "losses": user.losses,
        }
    )


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    # Check if nickname is takem
    if User.query.filter_by(username=username).first():
        return (jsonify({"error": "Nickname taken! Try another one."}),)

    # Hash and save password
    hashed_pw = generate_password_hash(password)
    new_user = User(username=username, password_hash=hashed_pw, money=1000)
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successful"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"Error": str(e)}), 500


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        session["user_id"] = user.id
        session["username"] = user.username
        return jsonify({"message": "Login successful", "username": user.username})

    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/")
@login_required
def home():
    # fetch the current userdata
    current_user = db.session.get(User, session["user_id"])
    return render_template("home.html", user=current_user)


@app.route("/api/hit", methods=["POST"])
@login_required
def hit():
    data = request.get_json()
    game_id = data.get("game_id")
    # Fetch the data
    game = db.session.get(Game, game_id)

    # Security check
    if not game:
        return jsonify({"error": "Game not found"}), 404
    if game.user_id != session["user_id"]:
        return jsonify({"error": "Unauthorized"}), 403
    if game.status != "active":
        return jsonify({"error": "Game is over"}), 400

    deck_obj = Deck()
    deck_obj.cards = [Card(c["rank"], c["suit"]) for c in game.deck]

    player_hand_obj = dict_to_hand(game.player_hand)

    # The action
    new_card = deck_obj.draw()
    player_hand_obj.add_card(new_card)
    score = player_hand_obj.get_value()

    # Updating the DB
    game.player_hand = object_to_dict(player_hand_obj)
    game.deck = [{"rank": c.rank, "suit": c.suit} for c in deck_obj.cards]

    # Flag to make SQLAlchemy notice the JSON change
    flag_modified(game, "player_hand")
    flag_modified(game, "deck")

    message = "Hit successful"
    if score > 21:
        game.status = "dealer_win"
        message = "Bust! You went over 21."
        user = db.session.get(User, session["user_id"])
        user.losses += 1

    db.session.commit()

    return jsonify(
        {
            "game_id": game.id,
            "player_hand": game.player_hand,
            "score": score,
            "status": game.status,
            "message": message,
        }
    )


@app.route("/api/deal", methods=["POST"])
@login_required
def deal():
    # Get the user and the bet
    user = db.session.get(User, session["user_id"])
    # Get bet from JSON body
    data = request.get_json()
    bet_amount = data.get("bet_amount", 10)
    # Can the user afford bet?
    if user.money < bet_amount:
        return jsonify({"Error": "You don't have enough money"}), 400
    user.money -= bet_amount
    # initialize the game object
    deck = Deck()
    player_hand = Hand()
    dealer_hand = Hand()

    # deal 2 cards for dealer and player
    for _ in range(2):
        player_hand.add_card(deck.draw())
        dealer_hand.add_card(deck.draw())

    new_game = Game(
        user_id=user.id,
        player_hand=object_to_dict(player_hand),
        dealer_hand=object_to_dict(dealer_hand),
        deck=[{"rank": c.rank, "suit": c.suit} for c in deck.cards],
        bet=bet_amount,
        status="active",
    )
    db.session.add(new_game)
    db.session.commit()
    return jsonify(
        {
            "message": "Game started",
            "game_id": new_game.id,
            "player_hand": new_game.player_hand,
            "dealer_card": new_game.dealer_hand[0],
            "user_money": user.money,
        }
    )


@app.route("/api/stand", methods=["POST"])
@login_required
def stand():
    data = request.get_json()
    game_id = data.get("game_id")
    # Fetch the truth
    game = db.session.get(Game, game_id)
    if not game or game.user_id != session["user_id"] or game.status != "active":
        return jsonify({"error": "Invalid game state"}), 400

    deck_obj = Deck()
    deck_obj.cards = [Card(c["rank"], c["suit"]) for c in game.deck]
    player_hand = dict_to_hand(game.player_hand)
    dealer_hand = dict_to_hand(game.dealer_hand)

    # The Dealer AI
    while dealer_hand.get_value() < 17:
        new_card = deck_obj.draw()
        dealer_hand.add_card(new_card)

    # Determine winner
    player_score = player_hand.get_value()
    dealer_score = dealer_hand.get_value()
    user = db.session.get(User, session["user_id"])

    result_message = ""

    if dealer_score > 21:
        game.status = "player_win"
        result_message = "Dealer busts! You win"
        user.wins += 1
        user.money += bet * 2
    elif dealer_score > player_score:
        game.status = "dealer_win"
        result_message = "Dealer win"
        user.losses += 1
    elif dealer_score < player_score:
        game.status = "player_wins"
        result_message = "Player wins"
        user.wins += 1
        user.money += bet * 2
    else:
        game.status = "push"
        result_message = "It's a tie"
        user.money += game.bet

    # Persistence
    game.dealer_hand = object_to_dict(dealer_hand)
    game.deck = [{"rank": c.rank, "suit": c.suit} for c in deck_obj.cards]

    # Force updates for JSON fields
    flag_modified(game, "dealer_hand")
    flag_modified(game, "deck")

    db.session.commit()

    return jsonify(
        {
            "game_id": game.id,
            "status": game.status,
            "dealer_hand": game.dealer_hand,
            "dealer_score": dealer_score,
            "player_score": player_score,
            "user_money": user.money,
            "message": result_message,
        }
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/game")
@login_required
def game_board():
    user = db.session.get(User, session["user_id"])
    player_data = session.get("player_hand")
    dealer_data = session.get("dealer_hand")
    result = session.get("result")
    game_over = session.get("game_over")

    if player_data is None:
        return redirect(url_for("home"))
    player_hand = dict_to_hand(player_data)
    dealer_hand = dict_to_hand(dealer_data)

    return render_template(
        "game.html",
        username=session.get("username"),
        user=user,
        player_hand=player_hand.hand,
        player_score=player_hand.get_value(),
        dealer_hand=dealer_data,
        dealer_score=dealer_hand.get_value(),
        result=session.get("result"),
        game_over=session.get("game_over"),
    )


@app.route("/api/test", methods=["GET"])
def test_connection():
    print("I AM ALIVE", flush=True)
    return jsonify({"message": "Python is talking to React"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
