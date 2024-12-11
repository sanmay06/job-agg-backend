from flask import jsonify

def register(username, email, password, users):
    if not username or not email or not password:
        return jsonify({"message": "Username, email, and password are required"}), 201

    if users.find_one({"username": username}):
        return jsonify({"message": "Username already exists"}), 201

    users.insert_one({"username": username, "password": password, "email": email})

    return jsonify({"message": "User successfully registered"}), 201

def login(username, password, users):
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = users.find_one({"username": username})

    if not user:
        return jsonify({"message": "Wrong username or password"}) 

    stored_password = user['password']

    if password != stored_password:
        return jsonify({"message": "Wrong username or password"})

    return jsonify({"message": "success"}), 200