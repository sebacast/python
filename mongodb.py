import pymongo
from bson.json_util import dumps
clienteMongo = "mongodb://localhost:27017/"
def find(db,col,query):
  #import pymongo
  myclient = pymongo.MongoClient(clienteMongo)
  mydb = myclient[db]
  mycol = mydb[col]
  if query=='todo':
    mydoc = mycol.find()
  else:
    mydoc = mycol.find(query)
  json_str = dumps(mydoc)
  myclient.close()
  return json_str

def contarDocumentos(db,col,query):
  #import pymongo
  myclient = pymongo.MongoClient(clienteMongo)
  mydb = myclient[db]
  mycol = mydb[col]
  mydoc = mycol.count_documents(query)
  json_str = dumps(mydoc)
  myclient.close()
  return json_str

def findMax(db,col,campo,valor,campoReq):
  myclient = pymongo.MongoClient(clienteMongo)
  mydb = myclient[db]
  mycol = mydb[col]
  if(campoReq == 'todo'):
    mydoc = mycol.find_one({campo:{"$regex": valor}}, sort=[("_id", -1)])
  else:
    mydoc = mycol.find_one({campo:{"$regex": valor}}, sort=[("_id", -1)])[campoReq]
 
  json_str = dumps(mydoc)
  myclient.close()
  return json_str

def insertOne(db,col,json):
  #import pymongo
  myclient = pymongo.MongoClient(clienteMongo)
  mydb = myclient[db]
  mycol = mydb[col]
  mycol.insert_one(json)
  myclient.close()

def updateOne(db,col,query,nuevo):
  myclient = pymongo.MongoClient(clienteMongo)
  mydb = myclient[db]
  mycol = mydb[col]
  newvalues = { "$set": nuevo }
  mycol.update_one(query, newvalues)
  myclient.close()

  #pruebas
  #pruebas
"""query = {"user_id" : "1"}
cant_accesos = contarDocumentos('pruebaDb','menu',query)
print(cant_accesos)
"""
  
