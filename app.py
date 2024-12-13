from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from userAuthentication import register, login
from profile import profileSend,profileReg
from jobs import internshala, adzuna, Times_job ,jobRapido

app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/miniproject"
mongo = PyMongo(app)
db = mongo.db

users = db.Users
jobsDB = db.jobs

@app.route("/home/<profile>", methods=['GET'])
def home(profile):
    username = request.args.get('user')
    result = users.find_one({"username": username, "profiles.name": profile}, {"profiles.$": 1})

    if result and "profiles" in result:
        profile_data = result["profiles"][0]
        title = profile_data['search']
        websites = profile_data['sites']
        location = profile_data['location']
        max = profile_data['max']
        min = profile_data['min']
        # Trigger scraping functions if necessary
        if "Internshala" in websites:
            internshala(title, jobsDB, location)
        if "Adzuna" in websites:
            adzuna(title, jobsDB, location)
        if "TimesJobs" in websites:
            Times_job(title, jobsDB, location)
        if "JobRapido" in websites:
            jobRapido(title, jobsDB, location)


        jobs = jobsDB.find_one({"category": title,"jobs.location":location,"jobs.salary":{"$gte":min,"$lte":max}}, {"_id": 0, "jobs": 1})
        
        #print("Jobs query result:", jobs)  

        if jobs:  
            job_entries = jobs.get("jobs", [])
            
            #print("Extracted jobs:", job_entries)  

            if job_entries: 
                if websites: 
                    filtered_jobs = [
                        job for job in job_entries if job["website"] in websites
                    ]
                    #print("Filtered jobs by websites:", filtered_jobs)  

                    if filtered_jobs:
                        return jsonify(filtered_jobs), 200
                    return jsonify({"message": "No jobs found for the given websites"}), 404

                return jsonify(job_entries), 200
            else:
                return jsonify({"message": "No jobs found in 'jobs'"}), 404
        else:
            return jsonify({"message": f"No data found for category '{title}'"}), 404

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
            #print(profile_data)
            return jsonify({"profile_data":profile_data,"msg": "found"}), 200
        return jsonify({"msg":"none"})
    else:
        data=request.json
        name = data.get('name')
        username = data.get('user')
        sites = data.get('sites')
        search = data .get('search')
        column = data.get('columns')
        min = data.get('min')
        max = data.get('max')
        location = data.get('location')
        return profileReg(username, sites, search, column, users, name, min, max, location)

@app.route("/register", methods=["POST"])
def reg():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    return register(username, email, password, users)
    

if __name__ == "__main__":
    app.run(debug=True)
