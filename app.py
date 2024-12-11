from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from userAuthentication import register, login
from profile import profileSend,profileReg
from jobs import internshala

app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/miniproject"
mongo = PyMongo(app)
db = mongo.db

users = db.Users
internshalla = db.internshala
@app.route("/home/<profile>", methods=['GET'])
def home(profile):
    username = request.args.get('user')
    result = users.find_one({"username":username,"profiles.name":profile},{"profiles.$":1})
    if result and "profiles" in result:
        result["_id"] = str(result["_id"])
        profile_data = result["profiles"][0]
        #print(profile_data)
        title = profile_data['search']
        internshala(title,internshalla)
        #print(title)
        jobs = mongo.db.internshala.find_one({"category": title}, {"_id": 0})
        if jobs:
            return jsonify(jobs[title]), 200
        else:
            return jsonify({"message": "No jobs found for the given title"}), 404
    return jsonify({"message": "Profile not found"}), 404

@app.route("/profile", methods=['GET'])
def profile():
    username = request.args.get("user")
    return profileSend(username, users)

@app.route("/login", methods=['POST'])
def log():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    return login(username, password, users)

@app.route("/profile/<name>",methods=["POST","GET"])
def updateProfile(name):
    if request.method == 'GET':
        username = request.args.get("user")
        result =  users.find_one({'profiles.name': name},{"profiles.$": 1})
        #print(result)
        if result and "profiles" in result:
            result["_id"] = str(result["_id"])
            profile_data = result["profiles"][0]
            print(profile_data)
            return jsonify({"profile_data":profile_data,"msg": "found"}), 200
        return jsonify({"msg":"none"})
    else:
        data=request.json
        name = data.get('name')
        username = data.get('user')
        sites = data.get('sites')
        search = data .get('search')
        column = data.get('columns')
        return profileReg(username, sites, search, column, users, name)        
    pass

@app.route("/register", methods=["POST"])
def reg():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    return register(username, email, password, users)
    

if __name__ == "__main__":
    app.run(debug=True)
