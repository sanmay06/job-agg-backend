from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo

app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = "mongodb+srv://sanmay:zGP6ju1GWAU5NIiK@cluster0.lbzvc.mongodb.net/mini-project"
mongo = PyMongo(app)
db = mongo.db

users = db.Users

@app.route("/test", methods=['GET'])
def test():
    return jsonify({"message": ["Hello world", "how are you today", "good?"]})

@app.route("/login", methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Find the user by username
    user = users.find_one({"username": username})

    # If user doesn't exist, return an error
    if not user:
        return jsonify({"message": "Wrong username or password"}), 401

    # Get the stored password (plain text)
    stored_password = user['password']

    # Compare the stored password with the entered password
    if password != stored_password:
        return jsonify({"message": "Wrong username or password"}), 401

    return jsonify({"message": "Logged in successfully"}), 200

@app.route("/register", methods=["POST"])
def reg():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required"}), 400

    # Check if the username already exists
    if users.find_one({"username": username}):
        return jsonify({"error": "Username already exists"}), 400

    # Insert the new user with plain text password into the database
    users.insert_one({"username": username, "password": password, "email": email})

    return jsonify({"message": "User successfully registered"}), 201

if __name__ == "__main__":
    app.run(debug=True)
