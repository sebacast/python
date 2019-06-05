import json
import pymysql.cursors
from bson.json_util import dumps

host = 'localhost'
user='root'
password=''
db='dtc'

def conn(host,user,password,db):
    connection = pymysql.connect(host=host,
                                     user=user,
                                     password=password,
                                     db=db,
                                     cursorclass=pymysql.cursors.DictCursor)
    return connection

def queryConPar(query,par):
    connection = conn(host,user,password,db)
    cur = connection.cursor()
    cur.execute(query, par)
    data = cur.fetchall()
    json_str = dumps(data)   
    connection.close()
    return data
    

def querySinPar(query):
    connection = conn(host,user,password,db)
    cur = connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    json_str = dumps(data)   
    connection.close()
    return data

def abmConPar(query,par):
    connection = conn(host,user,password,db)
    cur = connection.cursor()
    cur.execute(query, par)
    connection.commit()
    connection.close()

def ambSinPar(query):
    connection = conn(host,user,password,db)
    cur = connection.cursor()
    cur.execute(query)
    connection.commit()
    connection.close()

#pruebas

