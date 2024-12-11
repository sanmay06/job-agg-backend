from flask import jsonify

def profileSend(username, users):
    user = users.find_one({"username": username})
    if(user):
        #profile = user['profile']
        print( user['profile'])
        return jsonify(user['profile'])
    else:
        return jsonify({"error":"no user found"}), 400
    return jsonify({"error":"some error"}), 404

def profileReg(username, sites, search, column, users, name):
    query = {"$push":{'profiles':{'name':name,'search':search,'sites':sites,'column':column}}}
    print(column)
    result = users.update_one({'username':username},query)
    if(result.matched_count):
        users.update_one({'username':username},{'$push':{'profile':name}})
        return jsonify({'msg':'successfull'}), 200
    else:
        return jsonify({'msg':"error"}), 200
    pass