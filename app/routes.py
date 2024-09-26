from flask import Blueprint, request, jsonify
from app.models import db, User, Expense
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime

# Define the authentication blueprint
auth_bp = Blueprint('auth', __name__)

# Define the expense blueprint
expense_bp = Blueprint('expense', __name__)

# User registration route
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# User login route
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify({"token": access_token}), 200
    return jsonify({"message": "Invalid credentials"}), 401

# Add an expense route (requires JWT authentication)
@expense_bp.route('/add', methods=['POST'])
@jwt_required()
def add_expense():
    user_id = get_jwt_identity()
    data = request.get_json()

    new_expense = Expense(
        amount=data['amount'],
        category=data['category'],
        date=datetime.strptime(data['date'], '%Y-%m-%d'),
        description=data.get('description', ''),
        user_id=user_id
    )
    db.session.add(new_expense)
    db.session.commit()

    return jsonify({"message": "Expense added successfully"}), 201