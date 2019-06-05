from flask import Flask, request
import json
#import pymongo
from flask_cors import CORS
from bson.json_util import dumps
#from bson import regex
#import pymysql.cursors
#import jwt
import datetime
#import requests
import pytz
import mongodb
import mysql
import controlAcceso
app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/login",methods=['POST'])
def login():
    rq = request.json
    if 'id' in rq and 'token' in rq and 'tipo' in rq: #ingreso con Api FB o Google
        user_id = controlAcceso.getIdUsuarioAPI(rq['tipo'],rq['id'],rq['token'])

    elif 'email' in rq and 'clave' in rq: #ingreso con usuario y contraseña
        user_id = controlAcceso.getIdUsuarioEC(rq['email'],rq['clave'])

    else: #cualquier otro metodo es invalido
        user_id = 0

    json_str = controlAcceso.verificarAcceso(user_id) #respuesta en json
    #print(user_id)
    return json_str


@app.route("/menu")
def obtenerMenu():
    ###llave doble
    #reemplazar user_id para acceso con llave doble
    #user_id = eval(request.headers['Authorization'])['id']
    #user_id = controlAcceso.decodificarUserId(user_id)
    ###
    token =eval(request.headers['Authorization'])['token']
    #print(token)
    user_id = controlAcceso.verificarToken(token)
    try: 
        int(user_id) > 0
        json_str = mongodb.findMax('pruebaDb','menu','user_id',str(user_id),'menu') #traer menu
    except Exception: 
            json = {'aut': False}
            json_str=dumps(json) 
    #print(json_str)
    return json_str

@app.route("/geoloc",methods=['PUT'])
def geoloc():
    #
    zona = "America/Argentina/Buenos_Aires"
    token =eval(request.headers['Authorization'])['token']
    rq = request.json
    user_id = controlAcceso.verificarToken(token)
    print(rq['lat'])
    try:
        int(user_id) > 0
        #fyh = datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone("America/Argentina/Buenos_Aires")).strftime('%Y-%m-%d %H:%M:%S')
        fyh = fyh = datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone(zona))
        fyh = fyh.strftime('%Y-%m-%d %H:%M:%S')
        query = "insert into geoloc (id, idusu, lat, lon, fyh) values (0,%s,%s,%s,%s)"
        par = (str(user_id),str(rq['lat']),str(rq['lon']),str(fyh))
        mysql.abmConPar(query,par)
        json = {'aut': True}
        #json = {'user_id':str(user_id), 'geoloc':rq , 'fyh':fyh , 'fyhs':fyhs}
        #mongodb.insertOne('pruebaDb','geoloc',json)
    except Exception: 
            json = {'aut': False}
    json_str=dumps(json) 
    print(json_str)
    return json_str

@app.route("/geoloc")
def getGeo():
    json_str = mongodb.find('pruebaDb','geoloc',{'user_id':'1'})
    json_str = mysql.queryConPar('select g.idusu, DATE_FORMAT(g.fyh,%s) as fecha, g.lat,g.lon from geoloc g where g.idusu = %s',("%d/%m/%Y %H:%i",'1'))
    json_str = dumps(json_str)
    #json_str = json.loads(json_str)
    #json_str = dumps(json_str[0]['fyhs'])
    #json_str = datetime.fromtimestamp(json_str)
    #json_str = datetime.datetime.json_str.replace(microsecond=0).isoformat(' ')
  
    #json_str = str(json_str)
    #json_str = dumps(json_str['fyhs'])
    #print(json_str)
    return json_str

@app.route("/importar")
def impo():
    json_str = mongodb.find('pruebaDb','json','todo')
    return json_str

@app.route("/productos",methods=['POST'])
def prod():
    titulo = request.values['busqueda']
    query = {"$or": [ {"titulo":{"$regex": titulo, "$options": 'i'}}, {"categoria":{"$regex": titulo, "$options": 'i'}}, {"tienda": {"$regex": titulo, "$options": 'i'}} ]}
    json_str = mongodb.find('pruebaDb','productos',query)
    return json_str    

if __name__ == "__main__":
    app.run(debug=True,port=8888)
