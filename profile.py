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

def profileReg(username, sites, search, column, users, name, min_val, max_val, location):
    # Define the query to find the user by username
    user_query = {'username': username}
    
    # Check if the user exists
    user = users.find_one(user_query)
    
    if not user:
        return jsonify({'msg': "User not found"}), 404
    
    # Check if the profile already exists
    existing_profile = next((profile for profile in user.get('profiles', []) if profile['name'] == name), None)

    if existing_profile:
        # Update the existing profile
        update_query = {
            '$set': {
                'profiles.$.search': search,
                'profiles.$.sites': sites,
                'profiles.$.column': column,
                'profiles.$.min': min_val,
                'profiles.$.max': max_val
            }
        }
        result = users.update_one(
            {'username': username, 'profiles.name': name},
            update_query
        )
        
        if result.matched_count:
            return jsonify({'msg': 'Profile updated successfully'}), 200
        else:
            return jsonify({'msg': "Error updating profile"}), 500

    else:
        # If the profile does not exist, add a new one
        query = {
            "$push": {
                'profiles': {
                    'name': name,
                    'search': search,
                    'sites': sites,
                    'column': column,
                    'min': min_val,
                    'max': max_val,
                    'location':location
                }
            }
        }
        
        result = users.update_one(user_query, query)
        
        if result.matched_count:
            users.update_one(user_query, {'$push': {'profile': name}})
            return jsonify({'msg':'Profile added successfully'}), 200
        else:
            return jsonify({'msg': "Error adding profile"}), 500
    pass