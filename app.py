from flask import Flask, request
from flask_cors import CORS
import os
import psycopg2
from dotenv import load_dotenv
from jobs import internshala, adzuna, times_job, jobRapido

load_dotenv()

app = Flask(__name__)
CORS(app)

url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

insertUser = "INSERT INTO login (username, password, email) VALUES (%s, %s, %s)"

insertJobs =  """
    INSERT INTO jobs (job_title, link, title, companyname, salary, minsalary, maxsalary, location, website)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (link, location, title) DO NOTHING;
    """ 

createLogin = """
    CREATE TABLE IF NOT EXISTS login (
        username VARCHAR(20) PRIMARY KEY,
        password VARCHAR(20),
        email VARCHAR(30)
    );
"""

createProfiles = """
    CREATE TABLE IF NOT EXISTS profiles (
        id SERIAL PRIMARY KEY,
        name VARCHAR(20) ,
        username VARCHAR(20) ,
        FOREIGN KEY (username) REFERENCES login (username),
        internshalla BIT, 
        adzuna BIT,
        timesjob BIT,
        jobrapido BIT, 
        min INT,
        max INT,
        location VARCHAR(50),
        search VARCHAR(20)
        UNIQUE (name, username)
    );
"""
createJobs = """
    CREATE TABLE IF NOT EXISTS jobs (
        id SERIAL PRIMARY KEY,
        job_title varchar(20) ,
        link VARCHAR(500) ,
        title VARCHAR(20) ,
        website varchar(30) ,
        companyname VARCHAR(100) ,
        salary INT,
        minsalary INT,
        maxsalary INT,
        location VARCHAR(50) ,
        createddate DATE DEFAULT CURRENT_DATE
        UNIQUE (title, link, location)
    );
        
"""

checkPass = (    "SELECT password FROM login WHERE username = (%s)" )

get_profiles = "SELECT name FROM profiles WHERE username = (%s) "

get_all_profiles = "SELECT * FROM profiles WHERE username = (%s) "

@app.route("/")
def home():
    return "working"

@app.post("/reg")
def register():
    data = request.get_json()
    try:
        username = data["username"]
        password = data["password"]
        email = data["email"]

        with connection.cursor() as cursor:
            cursor.execute(createLogin)
            cursor.execute(insertUser, (username, password, email))
            connection.commit()

        return {"msg": "created successfully"}, 201
    except psycopg2.Error as e:
        connection.rollback()
        print(str(e))
        return {"error": str(e)}, 400

@app.post("/login")
def login():
    data = request.get_json()
    
    try:

        username = data["username"]
        passw = data["password"]

        with connection.cursor() as cursor:
            cursor.execute(checkPass, (username, ))
            password = cursor.fetchone()[0]
        
        if password is not None:
            if password == passw:
                return {"msg": "success",}, 201
            else:
                return {"msg": "Incorrect password or username"}, 400
    except psycopg2.Error as e:
        connection.rollback()
        print(str(e))
        return {"error": str(e)}, 400
    
@app.get("/getprofiles")
def getProfiles():
    user = request.args.get('user')
    try:
        with connection.cursor() as cursor:
            cursor.execute(createProfiles)
            cursor.execute(get_profiles, (user, ))
            names = cursor.fetchall()
        name = []
        for i in names:
            name.append(i[0])
        # print(name)
        return {"msg": "success", "names" : name}, 200
    except psycopg2.Error as e:
        connection.rollback()
        print(e)
        return {"error":str(e)}, 400

@app.get("/profile/<name>")
def getProfile(name):
    username = request.args.get('user')
    try:
        with connection.cursor() as cursor:
            cursor.execute(createProfiles)
            cursor.execute(get_all_profiles, (username,))
            profiles = cursor.fetchone()
            # print(profiles)
        return {"msg": "success", "profile" : profiles}, 200
    except psycopg2.Error as e:
        connection.rollback()
        print(e)
        return {"msg": "success", "error" : str(e)}, 200
    pass

def get_profile_id(username, old_name):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM profiles WHERE username = %s AND name = %s", (username, old_name))
        result = cursor.fetchone()
        return result[0] if result else None  # Returns ID if found, else None

@app.post("/profile/<profile_name>")
def postProfile(profile_name):
    data = request.get_json()
    try:
        username = data['user']
        new_name = data["name"]  # New name if updating
        search = data["search"]
        sites = data["sites"]
        min_salary = data['min']
        max_salary = data['max']
        print("Sites",sites)
        print("Adzuna" in sites)
        if "Adzuna" in sites:
            adzuna = '1'
        else:
            adzuna ='0'
        inter = '1' if "Internshala" in sites else '0'
        times = '1' if "TimesJobs" in sites else '0'
        jobr = '1' if "JobRapido" in sites else '0'
        location = data['location']

        with connection.cursor() as cursor:
            # Check if profile exists
            cursor.execute("SELECT id FROM profiles WHERE username = %s AND name = %s", (username, profile_name))
            profile = cursor.fetchone()

            if profile:
                # Profile exists -> Update it
                profile_id = profile[0]
                cursor.execute("""
                    UPDATE profiles 
                    SET name = %s, internshalla = %s, adzuna = %s, timesjob = %s, jobrapido = %s, 
                        min = %s, max = %s, location = %s, search = %s
                    WHERE id = %s
                """, (new_name, inter, adzuna, times, jobr, min_salary, max_salary, location, search, profile_id))
                connection.commit()
                return {"msg": "Profile updated successfully"}, 200
            else:
                # Profile doesn't exist -> Create a new one
                cursor.execute("""
                    INSERT INTO profiles (name, username, internshalla, adzuna, timesjob, jobrapido, min, max, location, search)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (new_name, username, inter, adzuna, times, jobr, min_salary, max_salary, location, search))
                connection.commit()
                return {"msg": "Profile created successfully"}, 201

    except psycopg2.Error as e:
        connection.rollback()
        print(e)
        return {"msg": "error", "error": str(e)}, 400

@app.get('/home/<profile>')
def PostJobs(profile):
    username = request.args.get('user')
    try: 
        with connection.cursor() as cursor:
            cursor.execute("SELECT location, search, internshalla, adzuna, timesjob, jobrapido FROM profiles WHERE name = %s AND username = %s", (profile, username))
            list = cursor.fetchone()

        if list is None:
            return {"msg": "failed to find the profile settings"}

        location = list[0]
        search = list[1]
        intern = list[2]
        adz = list[3]
        times = list[4]
        jobra = list[5]


        all_jobs = []
        web = []

        # Append job data as tuples
        if intern == '1':
            all_jobs.extend([tuple(job) for job in internshala(search, location)])
            web.append("Internshala")

        if adz == '1':
            all_jobs.extend([tuple(job) for job in adzuna(search, location)])
            web.append("Adzuna")

        if times == '1':
            all_jobs.extend([tuple(job) for job in times_job(search, location)])
            web.append("TimesJobs")

        if jobra == '1':    
            all_jobs.extend([tuple(job) for job in jobRapido(search, location)])
            web.append("JobRapido")


        # return all_jobs

        with connection.cursor() as cursor: 
            cursor.executemany(insertJobs, all_jobs)
            connection.commit()
        if web:
            placeholders = ', '.join(['%s'] * len(web))  
            query = f"SELECT * FROM jobs WHERE title = %s AND location = %s AND website IN ({placeholders})"
            
            with connection.cursor() as cursor:
                cursor.execute(query, (search, location, *web))  # Unpacking `web`
                jobs = cursor.fetchall()
        else:
            jobs = []

        return {"msg": "success", "new": len(all_jobs), 'jobs': jobs}, 200

    except psycopg2.Error as e:
        connection.rollback()
        print(e)
        return {"msg":"error", "error": str(e)}, 400
    
if __name__ == "__main__":
    app.run(debug=False)
