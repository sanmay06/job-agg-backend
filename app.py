from flask import Flask, request
from flask_cors import CORS
import os
import psycopg2
from dotenv import load_dotenv
from jobs import internshala, adzuna, times_job, jobRapido

load_dotenv()

app = Flask(__name__)
CORS(app)

url = "postgres://postgres.dambcrtyljufdjahsrxp:8blNKmCBGMWnRq1b@aws-0-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require"
connection = psycopg2.connect(url)

# username = "postgres"
# password = "dambcrtyljufdjdjahsrxp:8blNKmCBGMWnRq1b"
# host = "db.dambcrtyljufdjahsrxp.supabase.co"
# database_name = "postgres"
# port = 6543

# # Connect to the database
# connection = psycopg2.connect(
#     host=host,
#     database=database_name,
#     user=username,
#     password=password,
#     port = port,
#     sslmode="require"
# )

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
        search VARCHAR(20),
        UNIQUE (name, username)
    );
"""
createJobs = """
    CREATE TABLE IF NOT EXISTS jobs (
        id SERIAL PRIMARY KEY,
        job_title varchar(100) ,
        link VARCHAR(500) ,
        title VARCHAR(20) ,
        website varchar(100) ,
        companyname VARCHAR(100) ,
        salary INT,
        minsalary INT,
        maxsalary INT,
        location VARCHAR(100) ,
        createddate DATE DEFAULT CURRENT_DATE ,
        UNIQUE (title, link, location)
    );
        
"""

checkPass = (    "SELECT password FROM login WHERE username = (%s)" )

get_profiles = "SELECT name FROM profiles WHERE username = (%s) "

get_all_profiles = "SELECT * FROM profiles WHERE username = (%s) "


@app.route("/")
def home():
#     connection.rollback()
#     cursor = connection.cursor()
    
#     try:
#         cursor.execute(createJobs)
#         cursor.execute("alter table jobs alter column job_title type varchar(100)")
#         connection.commit()
#     except psycopg2.Error as e:
#         connection.rollback()
#         return str(e), 400
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
        return result[0] if result else None 

@app.post("/profile/<profile_name>")
def postProfile(profile_name):
    data = request.get_json()
    try:
        username = data['user']
        new_name = data["name"]  
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
            cursor.execute(createProfiles)
            cursor.execute("SELECT id FROM profiles WHERE username = %s AND name = %s", (username, profile_name))
            profile = cursor.fetchone()

            if profile:
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
@app.get('/scrape_jobs/internshala/<profile>')
def scrape_internshala(profile):
    username = request.args.get('user')
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT location, search, internshalla FROM profiles WHERE name = %s AND username = %s", (profile, username))
            profile_data = cursor.fetchone()

        if profile_data is None:
            return {"msg": "Profile not found"}, 404
        
        if(profile_data[2] == '0'):
            return {},200

        location, search, i = profile_data
        jobs = internshala(search, location)

        if jobs:
            with connection.cursor() as cursor:
                cursor.executemany(insertJobs, jobs)
                connection.commit()

        return {"msg": "Internshala scraping completed."}, 200

    except psycopg2.Error as e:
        connection.rollback()
        print("Error:", e)
        return {"msg": "error", "error": str(e)}, 400

@app.get('/scrape_jobs/adzuna/<profile>')
def scrape_adzuna(profile):
    username = request.args.get('user')
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT location, search, adzuna FROM profiles WHERE name = %s AND username = %s", (profile, username))
            profile_data = cursor.fetchone()

        if profile_data is None:
            return {"msg": "Profile not found"}, 404
        
        if(profile_data[2] == '0'):
            return {},200

        location, search, i = profile_data
        jobs = adzuna(search, location)

        if jobs:
            with connection.cursor() as cursor:
                cursor.executemany(insertJobs, jobs)
                connection.commit()

        return {"msg": "Adzuna scraping completed."}, 200

    except psycopg2.Error as e:
        connection.rollback()
        print("Error:", e)
        return {"msg": "error", "error": str(e)}, 400

@app.get('/scrape_jobs/timesjob/<profile>')
def scrape_timesjob(profile):
    username = request.args.get('user')
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT location, search, timesjob FROM profiles WHERE name = %s AND username = %s", (profile, username))
            profile_data = cursor.fetchone()

        if profile_data is None:
            return {"msg": "Profile not found"}, 404
        
        if(profile_data[2] == '0'):
            return {},200        

        location, search, i = profile_data
        jobs = times_job(search, location)

        if jobs:
            with connection.cursor() as cursor:
                cursor.executemany(insertJobs, jobs)
                connection.commit()

        return {"msg": "TimesJob scraping completed."}, 200

    except psycopg2.Error as e:
        connection.rollback()
        print("Error:", e)
        return {"msg": "error", "error": str(e)}, 400

@app.get('/scrape_jobs/jobrapido/<profile>')
def scrape_jobrapido(profile):
    username = request.args.get('user')
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT location, search, jobrapido FROM profiles WHERE name = %s AND username = %s", (profile, username))
            profile_data = cursor.fetchone()

        if profile_data is None:
            return {"msg": "Profile not found"}, 404

        if(profile_data[2] == '0'):
            return {},200

        location, search,i = profile_data
        jobs = jobRapido(search, location)

        if jobs:
            with connection.cursor() as cursor:
                cursor.executemany(insertJobs, jobs)
                connection.commit()

        return {"msg": "JobRapido scraping completed."}, 200

    except psycopg2.Error as e:
        connection.rollback()
        print("Error:", e)
        return {"msg": "error", "error": str(e)}, 400

@app.get('/fetch_jobs/<profile>')
def fetch_jobs(profile):
    username = request.args.get('user')
    try:
        with connection.cursor() as cursor:
            cursor.execute("Select search, location, internshalla, adzuna, timesjob, jobrapido from profiles where name = %s AND username = %s", (profile, username))
            websites = cursor.fetchone()
            if websites is None:
                return {"msg":"failed"}
            search, location, intern, adz, times, jobra = websites
            web = []
        if intern == '1':
            web.append("Internshala")

        if adz == '1':
            web.append("Adzuna")

        if times == '1':
            web.append("TimesJobs")

        if jobra == '1':    
            web.append("JobRapido")
        if web:
            placeholders = ', '.join(['%s'] * len(web))  
            query = f"SELECT * FROM jobs WHERE title = %s AND location = %s AND website IN ({placeholders})"
            
            with connection.cursor() as cursor:
                cursor.execute(query, (search, location, *web))  
                jobs = cursor.fetchall()
        else:
            jobs = []

        return {"msg": "success", 'jobs': jobs}, 200
        
        return {"msg": "Jobs fetched successfully.", "jobs": jobs}, 200
    
    except psycopg2.Error as e:
        print("Error:", e)
        return {"msg": "error", "error": str(e)}, 400
    

if __name__ == "__main__":
    app.run(debug=False)
