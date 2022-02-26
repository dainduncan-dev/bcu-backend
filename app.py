from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.sqlite")
CORS(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)

    def __init__(self, email, password, name):
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.name = name

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(12), nullable=True)
    description = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    def __init__(self, date, description, type, category, amount):
        self.date = date
        self.description = description
        self.type = type
        self.category = category
        self.amount = amount


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "email", "password", "name")

class TransactionSchema(ma.Schema):
    class Meta:
        fields = ("id", "date","description", "type", "category", "amount")

user_schema = UserSchema()
multiple_user_schema = UserSchema(many=True)

transaction_schema = TransactionSchema()
multiple_transaction_schema = TransactionSchema(many=True)


@app.route('/user/add', methods=["POST"])
def add_user():
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be JSON' )

    post_data = request.get_json()
    email = post_data.get("email")
    password = post_data.get("password")
    name = post_data.get("name")

    duplicate = db.session.query(User).filter(User.email == email).first()

    if duplicate != None:
        return jsonify("Error: That email is already registered.")

    encrypted_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email, encrypted_password, name)
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify("User has been created")

@app.route("/user/authenticate", methods=["POST"])
def authenticate_user():
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be JSON' )

    post_data = request.get_json()
    email = post_data.get('email')
    password = post_data.get('password')

    user = db.session.query(User).filter(User.email == email).first()

    if user is None:
        return jsonify('User not authenticated')

    if bcrypt.check_password_hash(user.password, password) == False:
        return jsonify('User not authenticated')

    return jsonify('User has been authenticated.')

@app.route("/user/get", methods=["GET"])
def get_all_users():
    all_users = db.session.query(User).all()
    return jsonify(multiple_user_schema.dump(all_users))

@app.route("/user/get/<email>", methods=["GET"])
def get_user_by_email():
    user = db.session.query(User).filter(User.email == email).first()

    return jsonify(user_schema.dump(user))

@app.route("/transactions/add", methods=["POST"])
def add_transaction():
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be JSON' )

    post_data = request.get_json()
    date = post_data.get("date")
    description = post_data.get("description")
    type = post_data.get("type")
    category = post_data.get("category")
    amount = post_data.get("amount")

    

    new_transaction = Transaction(date, description, type, category, amount)
    
    db.session.add(new_transaction)
    db.session.commit()

    return jsonify("Transaction has been created.")

@app.route("/transactions/get", methods=["GET"])
def get_all_transactions():
    all_transactions = db.session.query(Transaction).all()
    return jsonify(multiple_transaction_schema.dump(all_transactions))

@app.route("/transactions/get/<type>", methods=["GET"])
def get_transaction_by_type():
    transaction = db.session.query(Transaction).filter(Transaction.type == type).first()

    return jsonify(multiple_transaction_schema.dump(transaction))

if __name__ == '__main__':
    app.run(debug=True)