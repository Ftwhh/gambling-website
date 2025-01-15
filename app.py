
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gambling.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    is_owner = db.Column(db.Boolean, default=False)

class GameHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game = db.Column(db.String(50), nullable=False)
    result = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)

# Helper Functions
def add_user(username, password, is_owner=False):
    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(username=username, password=hashed_password, is_owner=is_owner)
    db.session.add(new_user)
    db.session.commit()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username already exists"}), 400
    add_user(data['username'], data['password'])
    return jsonify({"message": "User registered successfully"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        session['user_id'] = user.id
        session['is_owner'] = user.is_owner
        return jsonify({"message": "Login successful"})
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})

@app.route('/balance', methods=['GET'])
def get_balance():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401
    user = User.query.get(session['user_id'])
    return jsonify({"balance": user.balance})

@app.route('/blackjack', methods=['POST'])
def play_blackjack():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    user = User.query.get(session['user_id'])
    bet = request.json.get('bet')
    if bet > user.balance:
        return jsonify({"message": "Insufficient balance"}), 400

    user.balance -= bet

    player_score = random.randint(15, 21)
    dealer_score = random.randint(17, 21)
    result = ""

    if player_score > dealer_score or dealer_score > 21:
        result = "win"
        user.balance += bet * 2
    else:
        result = "lose"

    db.session.add(GameHistory(user_id=user.id, game="Blackjack", result=result, amount=bet))
    db.session.commit()
    return jsonify({"result": result, "player_score": player_score, "dealer_score": dealer_score, "balance": user.balance})

@app.route('/plinko', methods=['POST'])
def play_plinko():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    user = User.query.get(session['user_id'])
    bet = request.json.get('bet')
    if bet > user.balance:
        return jsonify({"message": "Insufficient balance"}), 400

    user.balance -= bet
    outcome = random.choices(["lose", "win", "jackpot"], weights=[70, 25, 5], k=1)[0]

    if outcome == "win":
        user.balance += bet * 1.5
    elif outcome == "jackpot":
        user.balance += bet * 10

    db.session.add(GameHistory(user_id=user.id, game="Plinko", result=outcome, amount=bet))
    db.session.commit()
    return jsonify({"result": outcome, "balance": user.balance})

@app.route('/owner/add_balance', methods=['POST'])
def add_balance():
    if 'user_id' not in session or not session.get('is_owner', False):
        return jsonify({"message": "Unauthorized"}), 401

    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    user.balance += data['amount']
    db.session.commit()
    return jsonify({"message": "Balance updated", "new_balance": user.balance})

if __name__ == '__main__':
    db.create_all()
    # Uncomment to create the owner account on first run
    # add_user("owner", "ownerpassword", is_owner=True)
    app.run(debug=True)
