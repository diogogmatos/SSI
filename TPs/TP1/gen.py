import bson

with open('database.bson', 'xb') as file:
    file.write(bson.BSON.encode({}))
