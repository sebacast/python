import jwt
import json
from bson.json_util import dumps
import datetime
import pytz
import requests
import mysql
import mongodb

def getIdUsuarioAPI(tipo,user_id,access_token):
    if tipo==1:#google
        par = (user_id,'idgoogle')
        #par2 = {'oauth_token': access_token}
        #url = "https://www.googleapis.com/oauth2/v2/userinfo"

    elif tipo==2:#facebook
        par = (user_id,'idfacebook')
        #par2 = {'access_token': access_token, 'fields':'name,email,picture'}
        #url ='https://graph.facebook.com/'+user_id
        
    query = "SELECT up.valor, u.id from usu_par up inner join usuarios_par usp on usp.id = up.idpar inner join usuarios u on u.id = up.idusu where up.valor = %s and usp.des= %s and up.estado = 1"
    try:
        res = mysql.queryConPar(query,par)
        if res[0]['valor'] == user_id:
            ##aca puede ir la captura de datos con getDatosApi si es el primer acceso
            return res[0]['id']
        else:
            return 0    
    except Exception:
        return 0

def getDatosApi(url,par):#funcion para recuperar los datos de la api
    """if tipo==1:#google
        par = {'oauth_token': access_token}
        url = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    elif tipo==2:#facebook
        par = {'access_token': access_token, 'fields':'name,email,picture'}
        url ='https://graph.facebook.com/'+user_id"""
    try:
        r = requests.get(url, params=par)# peticion de objeto auth
        if r.status_code == 200:#si la peticion es devuelta
            return r
    except Exception:
        return None

def validarUsrIdApi(user_id,par):
    query = "SELECT up.valor, u.id from usu_par up inner join usuarios_par usp on usp.id = up.idpar inner join usuarios u on u.id = up.idusu where up.valor = %s and usp.des= %s and up.estado = 1"
    try:
        res = mysql.queryConPar(query,par)
        if res[0]['valor'] == user_id:
            #print(res[0]['id'])
            return res[0]['id']
        else:
            return 0    
    except Exception:
        return 0

def getIdUsuarioEC(email,clave):
    query = "SELECT up.valor, up.idusu from usu_par up inner join usuarios_par usp on usp.id = up.idpar inner join usuarios u on u.id = up.idusu where (usp.des = 'email' and up.valor = %s) or (usp.des = 'clave' and up.valor = %s)"
    par = (email,clave)
    try:
        res = mysql.queryConPar(query,par)
        if res[0]['valor'] == email and res[1]['valor'] == clave:
            #print (res[0]['idusu'])
            return res[0]['idusu']
        else:
            return 0
    except NameError: return 0

def verificarAcceso(user_id):
    #print(user_id)
    query = {"user_id" : str(user_id)}
    cant_accesos = int(mongodb.contarDocumentos('pruebaDb','acc',query))
    secret = controlSecret(str(user_id),int(cant_accesos))
    if user_id > 0 and secret != None:
        json_str = dumps(generarToken(int(user_id),secret))
        CargarMenuEnMongo(str(user_id))
    else:
        json_str = dumps({'aut': False})
    #print(js)
    return json_str

def generarToken(user_id,secret):
    fyh = datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone("America/Argentina/Buenos_Aires")).strftime('%Y-%m-%d %H:%M:%S') 
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=3600),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id,
        'fyh': fyh,
    }
    token = jwt.encode(payload, secret, algorithm='HS256')
    token = token.decode('utf-8')
    #json = {'aut': True, 'token': token.decode('utf-8')}
    json = {'aut': True, 'token': token}
    mongodb.updateOne('pruebaDb','acc',{'secret':secret},{'token':token})
    return json
    ###llave doble
    #agregar 'id':user_id en el json para usar llave doble
    #user_id = jwt.encode({'user_id':user_id}, 'secreto', algorithm='HS256')
    #user_id = user_id.decode('utf-8')
    ###
    
    #print(token)
    

def controlSecret(user_id,cant_accesos):
    #cant_accesos = 0
    numero_reemplazo = 10
    activacion = divmod(cant_accesos, numero_reemplazo)
    if  activacion[1]==0 :#reemplazo del secret cada Nº cantidad de accesos
        secret = generarSecret()
        query = "update usuarios set secret = %s where id = %s"
        par = (secret,user_id)
        mysql.abmConPar(query,par)
        query = "select secret from usuarios where id = %s"
        try:
            secret = mysql.queryConPar(query,user_id)
            mongodb.insertOne('pruebaDb','acc',{'user_id':str(user_id), 'secret':secret[0]["secret"]})
            return secret[0]["secret"]
        except Exception:
            print('no se pudo obtener el secret')
            return None
    else:
        try:
            secret = mongodb.findMax('pruebaDb','acc','user_id',str(user_id),'todo')
            secret = json.loads(secret)
            return secret['secret']
        except Exception:
            return None

def generarSecret():
    from random import SystemRandom
    longitud = 18
    valores = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ<=>@#%&+"
    cryptogen = SystemRandom()
    p = ""
    while longitud > 0:
        p = p + cryptogen.choice(valores)
        longitud = longitud - 1
    return p


def CargarMenuEnMongo(user_id):
    query = "SELECT m.*,mo.descripcion as desmod FROM menu m inner join modulos mo on mo.id = m.idmod inner join permisos p on p.idmod = mo.id inner join usuarios u on u.id = p.idusu where u.id = %s and p.estado = 1 order by m.idmod"
    #par = (user_id)
    menu = mysql.queryConPar(query,user_id)
    menu = {'user_id':user_id, 'menu': menu}
    #print(menu)
    mongodb.insertOne('pruebaDb','menu', menu)

def verificarToken(token):
    secret = mongodb.find('pruebaDb','acc',{'token':token})
    secret = json.loads(secret)
    secret = secret[0]['secret']
    #print(secret)
    try:
        token = jwt.decode(token, secret, algorithms='HS256')
        #user_id = int(token['sub'])
        #print(token['sub'])
        return token['sub']
    except Exception:
        #jwt.ExpiredSignatureError
        return None

def decodificarUserId(user_id): #decodificador para llave doble
    user_id = jwt.decode(user_id, 'secreto', algorithms='HS256')
    return user_id
    #return user_id['user_id']



# prueba de funcion
#print(validarUsrClave('sebacastriv@gmail.com','1234'))
#print(validarIdApi('111327601781443169927'))


#print(controlSecret('1',8))


"""prueba = divmod(10,10)
print(prueba[1])"""

"""secret = mongodb.findMax('pruebaDb','acc','user_id','1')
secret = json.loads(secret)
print(secret['secret'])"""

"""json_str = mongodb.findMax('pruebaDb','menu','user_id','1') #traer menu
print(json_str)"""


"""query = {"user_id" : '1'}
#num = mongodb.contarDocumentos('pruebaDb','acc',query) + int(1)
print(mongodb.contarDocumentos('pruebaDb','acc',query))
#print(num)"""

#print(verificarAcceso(1))

"""print(verificarToken('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1NTk1MDQ3ODUsImlhdCI6MTU1OTUwMTE4NSwic3ViIjoxLCJmeWgiOiIyMDE5LTA2LTAyIDE1OjQ2OjI1In0.FtHIvJD-ZI3BVeTCjHINh37E1vKZdJNRXA_tp2jWHJA')
)"""

#print(mongodb.findMax('pruebaDb','menu','user_id','1','menu')) #traer menu




    
