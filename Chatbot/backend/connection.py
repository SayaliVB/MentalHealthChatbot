import json

with open('config.json') as config_file:
    data = json.load(config_file)

# database connection details

def connection():

    db = {}
    db['host'] = data['postgres']['host']
    db['database'] = data['postgres']['dbname']
    db['user'] = data['postgres']['user']
    db['password'] = data['postgres']['password']
    #print("DB details:")
    #print(db)
    return db