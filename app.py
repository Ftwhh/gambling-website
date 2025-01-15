from flask import Flask, request, jsonify, session, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gambling.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0)

def initialize_db():
    with app.app_context():
        db.create_all()

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Blackjack route
@app.route('/blackjack', methods=['POST'])
def play_blackjack():
    # Add your Blackjack game logic here
    return jsonify({"message": "Blackjack game is not implemented yet!"})

# Plinko route
@app.route('/plinko', methods=['POST'])
def play_plinko():
    # Add your Plinko game logic here
    return jsonify({"message": "Plinko game is not implemented yet!"})

# Admin route to add balance
@app.route('/admin/add_balance', methods=['POST'])
def admin_add_balance():
    if 'is_admin' in session and session['is_admin']:
        data = request.json
        username = data.get('username')
        amount = data.get('amount', 0)

        user = User.query.filter_by(username=username).first()
        if user:
            user.balance += amount
            db.session.commit()
            return jsonify({"message": f"Added {amount} to {username}'s balance."})
        else:
            return jsonify({"error": "User not found."}), 404
    return jsonify({"error": "Unauthorized."}), 403

# Admin login route
@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username == 'admin' and password == 'password':  # Change this to a secure login method
        session['is_admin'] = True
        return jsonify({"message": "Admin logged in successfully."})
    return jsonify({"error": "Invalid credentials."}), 401

# User balance check route
@app.route('/balance', methods=['GET'])
def check_balance():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user:
            return jsonify({"balance": user.balance})
    return jsonify({"error": "Unauthorized."}), 403

# Static folder setup
@app.route('/static/<path:path>')
def static_files(path):
    return app.send_static_file(path)

if __name__ == '__main__':
    initialize_db()
    app.run(debug=True)
