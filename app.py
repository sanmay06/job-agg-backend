from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo

app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/miniproject"
mongo = PyMongo(app)
db = mongo.db

users = db.Users
internshalla = db.internshala
@app.route("/home", methods=['GET'])
def home():
    job_list = internshalla.find()
    jobs = [{"title": job["title"], "company": job["company"],"link":job["link"],"location":job["location"],"salary":job["salary"]} for job in job_list]
    return jsonify(jobs)

@app.route("/profile", methods=['GET'])
def profile():
    username = request.args.get("user")
    user = users.find_one({"username": username})
    if(user):
        #profile = user['profile']
        print( user['profile'])
        return jsonify(user['profile'])
    else:
        return jsonify({"error":"no user found"}), 400
    
    return jsonify({"error":"some error"}), 404

@app.route("/login", methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = users.find_one({"username": username})

    if not user:
        return jsonify({"message": "Wrong username or password"}) 

    stored_password = user['password']

    if password != stored_password:
        return jsonify({"message": "Wrong username or password"})

    return jsonify({"message": "success"}), 200

@app.route("/profile/<name>",methods=["POST","GET"])
def updateProfile(name):
    username = request.args.get("user")
    query = {'username':username,'profile':name}
    user = internshalla.find_one(query)
    if request.method == 'GET':
        if(user):
            return jsonify({"msg":"none"})
        return jsonify(user)
    else:
        data=request.json
        
    pass

@app.route("/register", methods=["POST"])
def reg():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"message": "Username, email, and password are required"}), 201

    if users.find_one({"username": username}):
        return jsonify({"message": "Username already exists"}), 201

    users.insert_one({"username": username, "password": password, "email": email})

    return jsonify({"message": "User successfully registered"}), 201

if __name__ == "__main__":
    app.run(debug=True)
