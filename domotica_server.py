
# -*- coding: utf-8 -*- 
import serial
import time
from flask import request
from flask import jsonify
import os
from flaskext.mysql import MySQL
import subprocess
import hashlib
import pyglet
import time
import json as JSON
from subprocess import Popen, PIPE, STDOUT
import collections
import datetime
import locale
import thread,threading
from flask_cors import CORS, cross_origin
import sys
import signal
from picamera import PiCamera
from flask_session import Session
from sqlalchemy import create_engine
import sqlalchemy.pool as pool
#from espeak import espeak
from flask import Flask, render_template, session, redirect, url_for
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

#mysql= MySQL()
alarm_state = 0
#app.config['MYSQL_DATABASE_USER'] = 'root'
#app.config['MYSQL_DATABASE_PASSWORD'] = '1238'
#app.config['MYSQL_DATABASE_DB'] = 'domo_home'
#app.config['MYSQL_DATABASE_HOST'] = 'localhost'
#mysql.init_app(app)
engine = create_engine('mysql+pymysql://root:mypass@localhost/domo_home?charset=utf8',pool_size=5, max_overflow=10)
global conn
#con= mysql.connect()
global mypool
global temperatura
app.secret_key = '987321654011'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = '987321654011'
app.config.from_object(__name__)
Session(app)
reload(sys)
global ser
global th1
task_lights_on=False
task_lights_off=False
time_lights_on=""
time_lights_off=""
thread_on=True
global daemon_alarm_actived
appliance_task=0
temperatura="0";

try:
     #ser = serial.Serial(port='/dev/ttyACM0', baudrate = 9600, parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=2)
     
    ser =  serial.Serial('/dev/ttyACM0',9600,timeout=2)
     #serial.Serial(port='/dev/ttyACM0',parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)
except:
    print "serial not connected"


camera = PiCamera()

#VISTAS
@app.route("/session")
def SessionControl():
    if session.get('logged_in') != True:
        print("if Session")
        return redirect(url_for('login'))#redirect("http://localhost:5000/login", code=302)

@app.route("/")
def home():
    #return render_template('dashboard.html')
    if session.get('logged_in') == True:
        print("is logged")
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route("/login")
def login_get():
    print("login")
    if session.get('logged_in') == True:
        print("is logged")
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route("/login", methods=['POST'])
def login():
    if session.get('logged_in') == True:
        return redirect(url_for('dashboard'))
    
    conn = engine.connect()
    user=request.form['user']
    password=request.form['pass']
    h=hashlib.md5(password.encode())
    
    # query="select * from user where user = '{user}'  and password = '{password}'".format(user=user,password=h.hexdigest())
    query="select * from user u inner join role r on u.role_id = r.id where u.status = {activo} and u.user = '{user}' and u.password = '{password}'".format(activo=1,user=user,password=h.hexdigest())
    # query="select * from user u inner join role r on u.role_id = r.id where u.user = '{user}'".format(user=user)  #and u.password = '{password}'".format(user=user,password=h.hexdigest()) 
    
    result = conn.execute(query)
    #data=cursor.fetchall()

    userLogged = ""
    userRole = ""
    for row in result:
        userLogged = row[1]
        userRole = row[13]
    msg = collections.OrderedDict()
    conn.close()
    print(result)
    if userLogged!="":
        session['logged_in'] = True 
        session['userLogged'] = userLogged
        session['userRole'] = userRole #probar roles
        msg['status'] = 1
        msg['msg'] = 'Usuario ingresado correctamente.'
    else:
        msg['status'] = 0
        msg['msg'] = 'Usuario o contraseña incorrecta, está inactivo, o no cuenta con los permisos. Contacte con el Administrador.'
    res = JSON.dumps(msg)
    return res

@app.route("/logout")
def logout():
    session['logged_in'] = False
    session.clear()
    return redirect(url_for('login'))
@app.route("/dashboard")
def dashboard():
    if session.get('logged_in') != True:
        print("if Session")
        print(session)
        return redirect(url_for('login'))

    areaList = getActiveAreas()
    applianceList = getActiveAppliances()
    temperaturejson = JSON.loads(getTemperatura())['temperature']
    temperature = temperaturejson['value']
    humidity = JSON.loads(getHumedad())['humidity']['value']
    currentExpense = JSON.loads(getCurrentMonthExpense())
    locale.setlocale(locale.LC_ALL, 'an_ES.UTF-8')
    totalExpense = locale.format("%d", (currentExpense['totalExpense']), grouping=True)
    print("TEMP"+temperature)
    alarmStatus = getAlarmStatus()

    return render_template('dashboard.html',areas=areaList,appliances=applianceList,currentExpense=totalExpense,alarmStatus=alarmStatus,temperature=temperature,humidity=humidity,userLogged=session.get('userLogged'))

def getActiveAreas():
    conn = engine.connect()
    #cursor= conn.cursor()
    queryArea="select * from area where status = '{activo}'".format(activo=1)
    area_list = []
    print(len(area_list))
    area_rows=conn.execute(queryArea)
    #area_rows=cursor.fetchall()

    for row in area_rows:
        area = collections.OrderedDict()
        area['id'] = row[0]
        area['name'] = row[1]
        area['quantity'] = row[2]
        area['creation_date'] = str(row[3])
        area['status'] =  row[4 ]
        area['house_id'] =  row[5]
        print()
        area_list.append(area)
    conn.close()
    print(len(area_list))
    if len(area_list) > 0 and area_list != None:
        return area_list
    else:
        area_list.append("No hay elementos.")
        return area_list
def getActiveAppliances():
    conn = engine.connect()
    queryAppliance="select * from appliance where status = '{activo}'".format(activo=1)
    appliance_list = []
    appliance_rows=conn.execute(queryAppliance)
    #appliance_rows=cursor.fetchall()

    for row in appliance_rows:
        appliance = collections.OrderedDict()
        appliance['id'] = row[0]
        appliance['name'] = row[1]
        appliance['power'] = row[2]
        appliance['description'] = str(row[3])
        appliance['fee'] =  row[4 ]
        appliance['status'] =  row[5]
        appliance_list.append(appliance)
    conn.close()
    if len(appliance_list) > 0 and appliance_list != None:
        return appliance_list
    else:
        appliance_list.append("No hay elementos.")
        return appliance_list

#======== User services ============
@app.route("/user_index")
def userIndex():
    userRole = session.get('userRole')
    userCodeRole = isRoleValid(userRole)
    print(userRole)
    if session.get('logged_in') != True or userCodeRole == False:
        print("if Session")
        print(session)
        return redirect(url_for('login'))
    
    conn = engine.connect()
    query = "select * from user u inner join role r on r.id=u.role_id"

    rows=conn.execute(query)
    conn.close()
    #rows = cursor.fetchall()
 
    objects_list = []
    for row in rows:
                d = collections.OrderedDict()
                d['id'] = row[0]
                d['name'] = row[1]
                d['lastname'] = row[2]
                d['user'] = row[3]
                d['mail'] =  str(row[5]) #datetime.strftime("%Y-%m-%d %H:%M:%S")
                    #d['creation_date'] = row[6].strftime("%Y-%m-%d %H:%M:%S")
                d['birthdate'] = str(row[6])
                d['creationDate'] = str(row[7])
                d['status'] = row[8]
                d['phone'] = row[9]
                #d['role_id'] = row[9]
               
            
            #objects_list.append(d)

                # role = collections.OrderedDict()
                # role['id'] = 1
                # role['name'] = "admin"
                # d['role'] = role
                d['roleName'] = row[12]
                objects_list.append(d)

    #print(objects_list)
    #conn.close
    #usr  = {'name': 'gabi', 'lastname': 'cabrera' }
    if rows != None:
        return render_template('user_index.html',users=objects_list,userLogged=session.get('userLogged'))
    else:
        return render_template('user_index.html',"lista vacia")


@app.route("/sign_up")
def singUp():
    userRole = session.get('userRole')
    userCodeRole = isRoleAdmin()
    if session.get('logged_in') != True or userCodeRole == False:
        print("if Session")
        print(session)
        return redirect(url_for('login'))
    return render_template('sign_up.html',userLogged=session.get('userLogged'))


@app.route("/create_user", methods=['POST'])
def createUser():
    userRole = session.get('userRole')
    userCodeRole = isRoleAdmin()
    if session.get('logged_in') != True or userCodeRole == False:
        print("if Session")
        print(session)
        return redirect(url_for('login'))
    
    name=request.form['name']
    lastName=request.form['last-name']
    user=request.form['user']
    
    password=request.form['password']
    passHash=hashlib.md5(password.encode())
    convertedPass=passHash.hexdigest()

    phone=request.form['phone']
    email=request.form['email']
    roleId=request.form['user-role']
    
    birthDate=request.form['birthdate']
    status=request.form['user-active-radio']
    #   birthDate="2016-01-01"
    
    creationDate= time.strftime("%Y-%m-%d")
    
    
    query="insert into user (name,lastname,user,password,mail,birth_date,creation_date,status,phone,role_id)  values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    
    conn = engine.connect()
    data= conn.execute(query,(name,lastName,user,convertedPass,email,birthDate,creationDate,status,phone,roleId))
    #data=cursor.execute(query,("gabi","cabrera","gabi","123","fasdfa","2016-10-23","2016-01-02",1,"123456",1))
    #conn.commit()
    conn.close
    msg = collections.OrderedDict()
    if data !=None:
        print("create user")
        msg['status'] = 1
        msg['msg'] = "user successful created"
    else:
        msg = collections.OrderedDict()
        msg['status'] = 0
        msg['msg'] = "error, user not created"
    
    res = JSON.dumps(msg)
    return res


@app.route("/user_edit", methods=['GET'])
def userEdit():
    userRole = session.get('userRole')
    userCodeRole = isRoleAdmin()
    if session.get('logged_in') != True or userCodeRole == False:
        return redirect(url_for('login'))

    user_id = request.args.get('userId')
    d = collections.OrderedDict()
    
    query="select * from user u inner join role r on r.id=u.role_id where u.id = '{id}'  ".format(id=user_id)
    conn = engine.connect()    
    rows=conn.execute(query)
    conn.close()
    #rows=cursor.fetchall()
    #print(row)
    user = collections.OrderedDict()
    for row in rows:
            
                user['id'] = row[0]
                user['name'] = row[1]
                user['lastname'] = row[2]
                user['user'] = row[3]
                user['password'] = row[4]
                
                user['mail'] =  str(row[5]) #datetime.strftime("%Y-%m-%d %H:%M:%S")
                #d['creation_date'] = row[6].strftime("%Y-%m-%d %H:%M:%S")
                user['birthdate'] = str(row[6])
                user['status'] = row[8]
                user['phone'] = row[9]
                
                
                #objects_list.append(d)
                #role = collections.OrderedDict()
                #role['id'] = row[12]
                #role['name'] = row[13]
                user['roleId'] = row[11]
                user['roleName'] = row[12]
    
    return render_template('user_edit.html',user=user,userLogged=session.get('userLogged'))


@app.route("/user_edit", methods=['POST'])
def userSubmitEdit():
    userRole = session.get('userRole')
    userCodeRole = isRoleAdmin()
    if session.get('logged_in') != True or userCodeRole == False:
        return redirect(url_for('login'))

    id=request.form['user-id']
    name=request.form['name']
    lastName=request.form['last-name']
    user=request.form['user']
    password=request.form['password']
    phone=request.form['phone']
    email=request.form['email']
    roleId=request.form['user-role']
    
    birthDate=request.form['birthdate']
    status=request.form['user-status']
    passHash=hashlib.md5(password.encode())
    convertedPass=passHash.hexdigest()
    conn = engine.connect()  
    session.get('userLogged')
    queryPass="select password from user where id = '{id}'".format(id=id)
    rowPass=conn.execute(queryPass)
    conn.close()
    #rowPass=cursor.fetchall()
    psw = ""
    for row in rowPass:
        psw = row[0]
    updatePass = password
    if psw != password:
        updatePass = convertedPass

    #query="insert user (id,name,lastname,user,password,mail,birth_date,creation_date,status,phone,role_id)  values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    conn = engine.connect()
    data = conn.execute("""UPDATE user SET name=%s, lastname=%s, user=%s, password=%s, mail=%s, birth_date=%s, status=%s, phone=%s, role_id=%s WHERE id=%s""", (name, lastName, user, updatePass, email, birthDate, status, phone, roleId, id))
    
    
    #data= cursor.execute(query,(id,name,lastName,user,password,email,birthDate,status,phone,roleId))
    #conn.commit()
    conn.close()
    #conn.close
    msg = collections.OrderedDict()
    if data!=None:
        
        
        msg['status'] = 1
        msg['msg'] = "user successful edited"


    else:
        msg = collections.OrderedDict()
        msg['status'] = 0
        msg['msg'] = "error, user not edited"
    
    
    res = JSON.dumps(msg)
    return res


#=============== Area services =============
@app.route("/area_index")
def areaIndex():
    userRole = session.get('userRole')
    userCodeRole = isRoleAdmin()
    if session.get('logged_in') != True or userCodeRole == False:
        return redirect(url_for('login'))
   
    d = collections.OrderedDict()
    
    query="select * from area"
    objects_list = []
    conn = engine.connect()
    rows=conn.execute(query)
    conn.close()
    #rows=cursor.fetchall()
    #print(row)

    for row in rows:
                area = collections.OrderedDict()
                area['id'] = row[0]
                area['name'] = row[1]
                area['quantity'] = row[2]
                area['creation_date'] = str(row[3])

                area['status'] =  row[4]
                area['house_id'] =  row[5]

                objects_list.append(area)
    return render_template('area_index.html',areas = objects_list,userLogged=session.get('userLogged'))


@app.route("/area_create",methods=['GET'])
def registerArea():
    userRole = session.get('userRole')
    userCodeRole = isRoleAdmin()
    if session.get('logged_in') != True or userCodeRole == False:
        return redirect(url_for('login'))

    return render_template('area_create.html',userLogged=session.get('userLogged'))


@app.route("/area_create", methods=['POST'])
def submitArea():
    userRole = session.get('userRole')
    userCodeRole = isRoleAdmin()
    if session.get('logged_in') != True or userCodeRole == False:
        return redirect(url_for('login'))

    name=request.form['name']
    # quantity=request.form['quantity']
    status=request.form['area-status-radio']
    #description=request.form['description']
    creationDate=time.strftime("%Y-%m-%d");
    house_id=1;
    
    query="insert into area (name,creation_date,status,house_id)  values (%s,%s,%s,%s)"
    conn = engine.connect()
    data= conn.execute(query,(name,creationDate,status,house_id))
    
    #conn.commit()
    conn.close
    msg = collections.OrderedDict()
    if data !=None:
        msg['status'] = 1
        msg['msg'] = "user successful edited"
    else:
        msg = collections.OrderedDict()
        msg['status'] = 0
        msg['msg'] = "error, user not edited"
    
    res = JSON.dumps(msg)
    return res

@app.route("/area_edit",methods=['GET'])
def areaEdit():
    userRole = session.get('userRole')
    userCodeRole = isRoleAdmin()
    if session.get('logged_in') != True or userCodeRole == False:
        return redirect(url_for('login'))

    area_id = request.args.get('areaId')
    d = collections.OrderedDict()
    
    query="select * from area a where a.id = '{id}'  ".format(id=area_id)
    conn = engine.connect()    
    rows=conn.execute(query)
    #rows=cursor.fetchall()
    area = collections.OrderedDict()
    conn.close()
    for row in rows:
            
                area['id'] = row[0]
                area['name'] = row[1]
                # area['quantity'] = row[2]
                area['status'] = row[4]
    
    return render_template('area_edit.html',area=area,userLogged=session.get('userLogged'))


@app.route("/area_edit",methods=['POST'])
def areaSubmitEdit():
    userRole = session.get('userRole')
    userCodeRole = isRoleAdmin()
    if session.get('logged_in') != True or userCodeRole == False:
        return redirect(url_for('login'))

    id=request.form['area-id']
    name=request.form['name']
    # quantity=request.form['quantity']
    status=request.form['area-active-radio']
    conn = engine.connect() 
    data = conn.execute("""UPDATE area SET name=%s, status=%s WHERE id=%s""", (name, status, id))

    #conn.commit()
    conn.close
    
    msg = collections.OrderedDict()
    if data != None:
        msg['status'] = 1
        msg['msg'] = "user successful edited"
    else:
        msg = collections.OrderedDict()
        msg['status'] = 0
        msg['msg'] = "error, user not edited"
    
    res = JSON.dumps(msg)
    
    return res


#================= Appliance services ===============
@app.route("/appliance_index")
def applianceIndex():
    userRole = session.get('userRole')
    userCodeRole = isRoleAdmin()
    if session.get('logged_in') != True or userCodeRole == False:
        return redirect(url_for('login'))
   
    d = collections.OrderedDict()
    
    query="select ap.id, ap.name, ap.power, ap.fee, ap.description, ap.status, ap.creation_date, s.name, a.name, apt.name from appliance ap inner join sensor s on ap.sensor_id=s.id inner join area a on ap.area_id=a.id inner join appliance_type apt on ap.appliance_type_id=apt.id;"
    objects_list = []
    conn = engine.connect() 
    rows=conn.execute(query)
    #rows=cursor.fetchall()
    #print(row)
    conn.close()
    for row in rows:
                appliance = collections.OrderedDict()
                appliance['id'] = row[0]
                appliance['name'] = row[1]
                appliance['power'] = row[2]
                appliance['fee'] = row[3]
                appliance['description'] = row[4]

                appliance['status'] = row[5]
                appliance['creation_date'] = str(row[6])
                appliance['sensor'] = row[7]
                appliance['area'] = row[8]
                appliance['type'] = row[9]

                objects_list.append(appliance)
               
    return render_template('appliance_index.html',appliances=objects_list,userLogged=session.get('userLogged'))


@app.route("/appliance_create",methods=['GET'])
def registerAppliance():
    userRole = session.get('userRole')
    userCodeRole = isRoleAdmin()
    if session.get('logged_in') != True or userCodeRole == False:
        return redirect(url_for('login'))

    #cursor= conn.cursor()
    queryArea="select * from area"
    area_list = []
    conn = engine.connect() 
    area_rows=conn.execute(queryArea)
    #area_rows=cursor.fetchall()

    for row in area_rows:
        area = collections.OrderedDict()
        area['id'] = row[0]
        area['name'] = row[1]
        area_list.append(area)
    conn.close()

    conn = engine.connect() 
    queryApplianceType="select * from appliance_type"
    appliance_type_list = []
    appliance_type_rows=conn.execute(queryApplianceType)
    #appliance_type_rows=cursor.fetchall()

    for row in appliance_type_rows:
        appliance_type = collections.OrderedDict()
        appliance_type['id'] = row[0]
        appliance_type['name'] = row[1]
        appliance_type_list.append(appliance_type)
    conn.close()

    conn = engine.connect()
    querySensor="select * from sensor"
    sensor_list = []
    sensor_rows=conn.execute(querySensor)
    #sensor_rows=cursor.fetchall()

    for row in sensor_rows:
        sensor = collections.OrderedDict()
        sensor['id'] = row[0]
        sensor['name'] = row[1] + ", " + row[2]
        sensor_list.append(sensor)
    conn.close()
    #cursor= conn.cursor()
    return render_template('appliance_create.html',areas=area_list,sensors=sensor_list,appliance_types=appliance_type_list,userLogged=session.get('userLogged'))

    
@app.route("/appliance_create",methods=['POST'])
def submitAppliance():
    userRole = session.get('userRole')
    userCodeRole = isRoleAdmin()
    if session.get('logged_in') != True or userCodeRole == False:
        return redirect(url_for('login'))

    name=request.form['name']
    power=request.form['power']
    # fee=request.form['fee']
    status=request.form['appliance-status-radio']
    description=request.form['description']
    creationDate=time.strftime("%Y-%m-%d")
    sensor_id=request.form['sensor']
    area_id=request.form['area']#4;
    appliance_type_id=request.form['type-appliance']#1;

    conn = engine.connect()
    query="insert into appliance (name,power,description,status,creation_date,sensor_id,area_id,appliance_type_id)  values (%s,%s,%s,%s,%s,%s,%s,%s)"
    data= conn.execute(query,(name,power,description,status,creationDate,sensor_id,area_id,appliance_type_id))
    #conn.commit()
    conn.close()

    conn = engine.connect()
    queryApplianceQuantity = "select a.appliance_quantity from area a inner join appliance ap on a.id = ap.area_id where ap.area_id = '{id}'  ".format(id=area_id)
    print(queryApplianceQuantity)
    applianceQuantity = conn.execute(queryApplianceQuantity)
    conn.close()

    conn = engine.connect()
    newQuantity = applianceQuantity + 1
    print(newQuantity)
    dataUpdateArea = conn.execute("""UPDATE area SET appliance_quantity=%s WHERE id=%s""", (newQuantity, area_id))    
    print(dataUpdateArea)
    #conn.commit()
    conn.close()
    #conn.close
        
    msg = collections.OrderedDict()
    
    if data !=None:
        msg['status'] = 1
        msg['msg'] = "user successful edited"
    else:
        msg = collections.OrderedDict()
        msg['status'] = 0
        msg['msg'] = "error, user not edited"
    
    res = JSON.dumps(msg)

    return res


@app.route("/appliance_edit",methods=['GET'])
def applianceEdit():
    userRole = session.get('userRole')
    userCodeRole = isRoleAdmin()
    if session.get('logged_in') != True or userCodeRole == False:
        return redirect(url_for('login'))

    appliance_id = request.args.get('applianceId')

    conn = engine.connect()
    query="select ap.id, ap.name, ap.power, ap.fee, ap.description, ap.status, ap.creation_date, s.id, a.id, apt.id from appliance ap inner join sensor s on ap.sensor_id=s.id inner join area a on ap.area_id=a.id inner join appliance_type apt on ap.appliance_type_id=apt.id where ap.id = '{id}'; ".format(id=appliance_id)
    appliance_rows=conn.execute(query)
    conn.close()
    appliance = collections.OrderedDict()
    print(appliance_rows)

    for row in appliance_rows:
        appliance['id'] = row[0]
        appliance['name'] = row[1]
        appliance['power'] = row[2]
        # appliance['fee'] = row[3] no editable
        appliance['description'] = row[4]

        appliance['status'] = row[5]
        appliance['creation_date'] = str(row[6])
        appliance['sensorId'] = row[7]
        appliance['areaId'] = row[8]
        appliance['typeId'] = row[9]
    #cursor.close()
    conn = engine.connect()
    queryArea="select * from area"
    area_list = []
    area_rows=conn.execute(queryArea)
    #area_rows=cursor.fetchall()

    for row in area_rows:
        area = collections.OrderedDict()
        area['id'] = row[0]
        area['name'] = row[1]
        area_list.append(area)
    conn.close()

    conn = engine.connect()
    queryApplianceType="select * from appliance_type"
    appliance_type_list = []
    appliance_type_rows=conn.execute(queryApplianceType)
    #appliance_type_rows=cursor.fetchall()

    for row in appliance_type_rows:
        appliance_type = collections.OrderedDict()
        appliance_type['id'] = row[0]
        appliance_type['name'] = row[1]
        appliance_type_list.append(appliance_type)
    conn.close()

    conn = engine.connect()
    querySensor="select * from sensor"
    sensor_list = []
    sensor_rows=conn.execute(querySensor)
    #sensor_rows=cursor.fetchall()

    for row in sensor_rows:
        sensor = collections.OrderedDict()
        sensor['id'] = row[0]
        sensor['name'] = row[1] + ", " + row[2]
        sensor_list.append(sensor)
    conn.close()
    #cursor= conn.cursor()
    return render_template('appliance_edit.html',appliance=appliance,areas=area_list,sensors=sensor_list,appliance_types=appliance_type_list,userLogged=session.get('userLogged'))


@app.route("/appliance_edit",methods=['POST'])
def submitApplianceEdit():
    userRole = session.get('userRole')
    userCodeRole = isRoleAdmin()
    if session.get('logged_in') != True or userCodeRole == False:
        print("if Session")
        print(session)
        return redirect(url_for('login'))

    id=request.form['appliance-id']
    name=request.form['name']
    power=request.form['power']
    # fee=request.form['fee'] no es editable
    status=request.form['appliance-status-radio']
    description=request.form['description']
    #creationDate=time.strftime("%Y-%m-%d")
    sensor_id=request.form['sensor']
    area_id=request.form['area']#4;
    appliance_type_id=request.form['type-appliance']#1;

    
    #Obtener area_id para comparar si se edito o no el area y asi modificar el appliance_quantity, en las areas involucradas
    conn = engine.connect()
    queryCurrentAreaId = "select ap.area_id from appliance ap where ap.id = '{id}' ".format(id=id)
    currentAreaId = 0
    currentArea_rows=conn.execute(queryCurrentAreaId)
    #currentArea_rows=cursor.fetchall()
    print(currentArea_rows)
    for row in currentArea_rows:
        currentAreaId = row[0]
    conn.close()
    # print(currentAreaId)
    #updateAppQuantity = False
    
    conn = engine.connect()
    data = conn.execute("""UPDATE appliance SET name=%s, power=%s, status=%s, description=%s, sensor_id=%s, area_id=%s, appliance_type_id=%s WHERE id=%s""", (name, power, status, description, sensor_id, area_id, appliance_type_id, id))
    conn.close()
    # print(area_id)
    #Entra cuando no deberia
    if (str(currentAreaId) != area_id):

        #Obtener appliance quantity para sumar en areas.
        conn = engine.connect()
        queryApplianceQuantitySumar = "select a.appliance_quantity from area a inner join appliance ap on a.id = ap.area_id where ap.area_id = '{id}'  ".format(id=area_id)
        applianceQuantitySumar = 0
        quantitySuma_rows=conn.execute(queryApplianceQuantitySumar)
        #quantitySuma_rows=cursor.fetchall()
        for row in quantitySuma_rows:
            applianceQuantitySumar = row[0]
        print(applianceQuantitySumar)
        conn.close()

        #Se actualiza el valor de appliance_quantity en area al que se agrega.
        conn = engine.connect()
        newQuantitySumar = applianceQuantitySumar + 1
        print("quantity suma: ")
        print(newQuantitySumar)
        dataUpdateAreaSuma = conn.execute("""UPDATE area SET appliance_quantity=%s WHERE id=%s""", (newQuantitySumar, area_id))    
        print(dataUpdateAreaSuma)
        conn.close()


        #Obtener appliance quantity para restar en areas.
        conn = engine.connect()
        queryApplianceQuantityRestar = "select a.appliance_quantity from area a inner join appliance ap on a.id = ap.area_id where ap.area_id = '{id}'  ".format(id=currentAreaId)
        applianceQuantityRestar = 0
        quantityResta_rows=conn.execute(queryApplianceQuantityRestar)
        #quantityResta_rows=conn.fetchall()
        for row in quantityResta_rows:
            applianceQuantityRestar = row[0]
        print(applianceQuantityRestar)
        conn.close()

        #Se actualiza el valor de appliance_quantity en el area del que se quita.
        conn = engine.connect()
        newQuantityRestar = applianceQuantityRestar - 1
        print("quantity resta: ")
        print(newQuantityRestar)
        dataUpdateAreaResta = conn.execute("""UPDATE area SET appliance_quantity=%s WHERE id=%s""", (newQuantityRestar, currentAreaId))    
        conn.close()
    # conn.commit()
    #cursor.close()

    msg = collections.OrderedDict()
    
    if data == 1:
        msg['status'] = 1
        msg['msg'] = "user successful edited"
    else:
        msg = collections.OrderedDict()
        msg['status'] = 0
        msg['msg'] = "error, user not edited"
    
    res = JSON.dumps(msg)

    return res
#Funcion para validar role admin y familia del usuario.
def isRoleValid(userRole):
    query = "select code from role where code = '{admin}' or code='{family}'".format(admin='A',family='F')
    conn = engine.connect()
    codeRow=conn.execute(query)
    #codeRow = cursor.fetchall()
    role = False
    userCodeRole = ""
    for code in codeRow:
        if userRole == code[0]:
            role = True
            break
        # userCodeRole = code[0]

    conn.close()
    return role
#Funcion para validar role admin del usuario.
def isRoleAdmin():
    userRole = session.get('userRole')
    query = "select code from role where code = '{admin}'".format(admin='A')
    conn = engine.connect()
    codeRow=conn.execute(query)
    #codeRow = cursor.fetchall()
    print(codeRow)
    roleAdmin = ""
    for code in codeRow:
        roleAdmin = code[0]

    conn.close()
    if roleAdmin == userRole:
        return True
    else:
        return False
#========= Tasks services ===========
@app.route("/task_index")
def taskIndex():
    userRole = session.get('userRole')
    userCodeRole = isRoleValid(userRole)
    print(userRole)
    if session.get('logged_in') != True or userCodeRole == False:
        print("if Session")
        print(session)
        return redirect(url_for('login'))

    areasList = getActiveAreas()
    # cursor = conn.cursor()
    # query = "select * from task"

    # cursor.execute(query)
    # cursor.close()
    # rows = cursor.fetchall()
 
    # objects_list = []
    # for row in rows:
    #             d = collections.OrderedDict()
    #             d['id'] = row[0]
    #             d['name'] = row[1]
    #             d['description'] = row[2]
    #             d['creationDate'] = str(row[3])
    #             d['time'] = str(row[4]) 
    #             d['status'] = row[5]
    #             objects_list.append(d)

    # cursor.close()

    #conn.commit()
    #print(objects_list)
    #conn.close
    if areasList != None:
        return render_template('task_index.html',areas= areasList,userLogged=session.get('userLogged'))
    else:
        return render_template('task_index.html',"lista vacia")

#API
@app.route("/arduino/lights", methods=['GET'])
def arduinoLights():
	status_light="error"
	action = request.args.get('action')
	appliance_id = request.args.get('appliance_id')
	transactionId = 0
	json = collections.OrderedDict()
	status=0
	if action=='status':
	    print("status")
	    ser.write('status')
	    status_light=ser.readline()
	    #while True:
	    print(status_light)
	if action=='light_on_l1':
	    print("light_on  lamp 1")
	    ser.write('LIGHT_ON_L1')
	    status_light='light_on_l1'
	   
	    
	if action=='light_off_l1':
      	    print('light_off lamp 1')
	    ser.write('LIGHT_OFF_L1')
	    status_light='light_off_l1'

	if action=='light_on_l2':
	    print("light_on  lamp 2")
	    ser.write('LIGHT_ON_L2')
	    status_light='light_on_l2'
	   
	    
	if action=='light_off_l2':
      	    print('light_off lamp 2')
	    ser.write('LIGHT_OFF_L2')
	    status_light='light_off_l2'	   

	

	conn = engine.connect()
	rows=conn.execute("select id from transaction where appliance_id = {appliance_id} and status = {status}".format(appliance_id=appliance_id,status=status)) 
	#rows = cursor.fetchall()#verifica si la luz esta encendida
	conn.close()
	for row in rows:
		transactionId=row[0]

	if transactionId!=0:#si la luz ya esta encendida y action es light_off actualiza el estado a apagado
		if action=='light_off_l1' or action=='light_off_l2':
			conn = engine.connect()
			conn.execute("""UPDATE transaction SET datetime_off=%s,status=%s WHERE id = %s""", (time.strftime("%Y-%m-%d %I:%M:%S"),1,transactionId))
			#conn.commit()                           
			conn.close()

	else:
		if action=='light_on_l1' or action=='light_on_l2':#inserta solo si action es encender luz
			conn = engine.connect()
			query="insert into transaction ( name , datetime_on , status , appliance_id,datetime_off )  values (%s,%s,%s,%s,%s)"    
			data= conn.execute(query,("lampara", time.strftime("%Y-%m-%d %I:%M:%S"),0, appliance_id,None))
			#conn.commit()
	    	conn.close()
    
	if status_light=='light_on_l1' or status_light=='light_off_l1' or status_light=='light_on_l2'or status_light=='light_off_l2':
		json["status"] = 1
		
	json["msg"] = status_light
	
	
 	return jsonify(json)
@app.route("/getCurrentMonthExpense", methods=['GET'])
def getCurrentMonthExpense():
	conn = engine.connect()
	query="select (TIMESTAMPDIFF(SECOND,datetime_on, datetime_off)/60/60)*power*fee as expense from transaction t inner join appliance a on t.appliance_id=a.id  where month(datetime_off)=month(now()) and year(datetime_off)=year(now())"
	data= conn.execute(query)
	#rows = cursor.fetchall()
	json = collections.OrderedDict()
	totalExpense=0
	
	for row in data:
		totalExpense+=row[0]

	json["msg"] = "ok"
	json["status"] = 1
	json["totalExpense"] = int(totalExpense)
	conn.close()
	return JSON.dumps(json)

@app.route("/get_expense_by_area", methods=['POST'])
def getExpenseByArea():
	conn = engine.connect()
	start_date = request.form['start_date']
	end_date = request.form['end_date']
	area_id = request.form['area_id']
	json = collections.OrderedDict()
	
	query="select areaExpense('"+start_date+"','"+end_date+"',"+area_id+")"
	rows= conn.execute(query)
	#rows = cursor.fetchall()
	
	for row in rows:
			json["status"] = 1
			json["result"] = row[0]
	conn.close()
	return jsonify(json)

@app.route("/get_expense_by_appliance", methods=['POST'])
def getExpenseByAppliance():
	conn = engine.connect()
	start_date = request.form['start_date']
	end_date = request.form['end_date']
	appliance_id = request.form['appliance_id']
	json = collections.OrderedDict()

	query="select applianceExpense('"+start_date+"','"+end_date+"',"+appliance_id+")"
	rows= conn.execute(query)
	#rows = cursor.fetchall()
	
	for row in rows:
			json["status"] = 1
			json["result"] = row[0]

	conn.close()
	return jsonify(json)
@app.route("/get_total_expense", methods=['POST'])
def getTotalExpense():
	conn = engine.connect()
	start_date = request.form['start_date']
	end_date = request.form['end_date']
	json = collections.OrderedDict()
	print(end_date)
	print(start_date)

	query="select totalExpense('"+start_date+":00:00','"+end_date+":23:59')"
	rows= conn.execute(query)
	#rows = cursor.fetchall()
	
	for row in rows:
			json["status"] = 1
			json["result"] = row[0]

	conn.close()
	return jsonify(json)
@app.route("/get_monthly_expense_by_area", methods=['GET'])
def get_monthly_expense_by_area():
	conn = engine.connect()
	status=1
	msg='succcess'
	month_num = request.args.get('month')
	if (month_num==None or month_num.strip()==""):
		query="select sum(TIMESTAMPDIFF(SECOND,datetime_on, datetime_off)/60/60)*power*fee as expense,ar.name as area_name from transaction t inner join appliance a on t.appliance_id=a.id inner join area ar on ar.id=a.area_id  where month(datetime_off)=month(now()) and year(datetime_off)=year(now()) group by ar.name;"
	else:
		query="select sum(TIMESTAMPDIFF(SECOND,datetime_on, datetime_off)/60/60)*power*fee as expense,ar.name as area_name from transaction t inner join appliance a on t.appliance_id=a.id inner join area ar on ar.id=a.area_id  where month(datetime_off)="+month_num+" and year(datetime_off)=year(now()) group by ar.name;"
	json = collections.OrderedDict()
	obj = collections.OrderedDict()

	
	rows= conn.execute(query)
	#rows = cursor.fetchall()
	expense_list = []
	for row in rows:
		
			obj = collections.OrderedDict()
			
			obj["expense"] = row[0]
			obj["area_name"] = row[1]
		
			expense_list.append(obj)
			
	conn.close()
	json['status']=status
	json['msg']=msg
	json['expense_list']=expense_list
	return jsonify(json)

@app.route("/get_monthly_expense_by_appliance", methods=['GET'])
def get_monthly_expense_by_appliance():
	conn = engine.connect()
	month_num = request.args.get('month')
	if (month_num==None or month_num.strip()==""):
		month_num="month(now())"
	json = collections.OrderedDict()
	

	query="select sum(TIMESTAMPDIFF(SECOND,datetime_on, datetime_off)/60/60)*power*fee as expense,a.name as area_name from transaction t inner join appliance a on t.appliance_id=a.id where month(datetime_off)="+month_num+" group by a.name;"
	rows= conn.execute(query)
	#rows = cursor.fetchall()
	server_list = []
	for row in rows:
		
			json = collections.OrderedDict()
			
			json["expense"] = row[0]
			json["appliance_name"] = row[1]
		
			server_list.append(json)
			
	conn.close()
	return JSON.dumps(server_list)

@app.route("/get_monthly_expenses", methods=['GET']) 
def get_monthly_expenses():
	conn = engine.connect()
	year = request.args.get('year')
	if year == None or year =="":
		year="year(now())"
	json = collections.OrderedDict()
	query="""select  IFNULL(sum(case when month(datetime_off)=1 then (TIMESTAMPDIFF(SECOND,datetime_on, datetime_off)/60/60)*power*fee end),0) As Enero, 
	 IFNULL(sum(case when month(datetime_off)=2 then (TIMESTAMPDIFF(SECOND,datetime_on, datetime_off)/60/60)*power*fee end),0) As Febrero, 
	 IFNULL(sum(case when month(datetime_off)=3 then (TIMESTAMPDIFF(SECOND,datetime_on, datetime_off)/60/60)*power*fee end),0) As Marzo, 
	 IFNULL(sum(case when month(datetime_off)=4 then (TIMESTAMPDIFF(SECOND,datetime_on, datetime_off)/60/60)*power*fee end),0) As Abril, 
	 IFNULL(sum(case when month(datetime_off)=5 then (TIMESTAMPDIFF(SECOND,datetime_on, datetime_off)/60/60)*power*fee end),0) As Mayo, 
	 IFNULL(sum(case when month(datetime_off)=6 then (TIMESTAMPDIFF(SECOND,datetime_on, datetime_off)/60/60)*power*fee end),0) As Junio, 
	 IFNULL(sum(case when month(datetime_off)=7 then (TIMESTAMPDIFF(SECOND,datetime_on, datetime_off)/60/60)*power*fee end),0) As Julio, 
	 IFNULL(sum(case when month(datetime_off)=8 then (TIMESTAMPDIFF(SECOND,datetime_on, datetime_off)/60/60)*power*fee end),0) As Agosto, 
	 IFNULL(sum(case when month(datetime_off)=9 then (TIMESTAMPDIFF(SECOND,datetime_on, datetime_off)/60/60)*power*fee end),0) As Septiembre, 
	IFNULL(sum(case when month(datetime_off)=10 then (TIMESTAMPDIFF(SECOND,datetime_on, datetime_off)/60/60)*power*fee end),0) As Octubre,
	IFNULL(sum(case when month(datetime_off)=11 then (TIMESTAMPDIFF(SECOND,datetime_on, datetime_off)/60/60)*power*fee end),0) As Noviembre,
	IFNULL(sum(case when month(datetime_off)=12 then (TIMESTAMPDIFF(SECOND,datetime_on, datetime_off)/60/60)*power*fee end),0) As Diciembre
	 from transaction  t inner join appliance a on t.appliance_id=a.id where EXTRACT(YEAR FROM datetime_off)="""+year
	rows= conn.execute(query)
	#rows = cursor.fetchall()
	server_list = []
	
	for row in rows:
		
			json = collections.OrderedDict()
			json["month"] = "Enero"
			json["expense"] = row[0]

			server_list.append(json)

			json = collections.OrderedDict()
			json["month"] = "Febrero"
			json["expense"] = row[1]
			server_list.append(json)

			json = collections.OrderedDict()
			json["month"] = "Marzo"
			json["expense"] = row[2]
			server_list.append(json)

			json = collections.OrderedDict()
			json["month"] = "Abril"
			json["expense"] = row[3]
			server_list.append(json)

			json = collections.OrderedDict()
			json["month"] = "Mayo"
			json["expense"] = row[4]
			server_list.append(json)

			json = collections.OrderedDict()
			json["month"] = "Junio"
			json["expense"] = row[5]
			server_list.append(json)

			json = collections.OrderedDict()
			json["month"] = "Julio"
			json["expense"] = row[6]
			server_list.append(json)

			json = collections.OrderedDict()
			json["month"] = "Agosto"
			json["expense"] = row[7]
			server_list.append(json)

			json = collections.OrderedDict()
			json["month"] = "Septiembre"
			json["expense"] = row[8]
			server_list.append(json)

			json = collections.OrderedDict()
			json["month"] = "Octubre"
			json["expense"] = row[9]
			server_list.append(json)

			json = collections.OrderedDict()
			json["month"] = "Noviembre"
			json["expense"] = row[10]
			server_list.append(json)
			
			json = collections.OrderedDict()
			json["month"] = "Diciembre"
			json["expense"] = row[11]
			server_list.append(json)

			
	conn.close()
	return JSON.dumps(server_list)
@app.route("/get_all_expenses", methods=['GET'])
def get_all_expenses():
	conn = engine.connect()

	json = collections.OrderedDict()

	query="""select datetime_on,datetime_off, (TIMESTAMPDIFF(SECOND,datetime_on, datetime_off)/60/60)*power*fee as expense,a.name,ar.name,
		CONCAT( MOD(HOUR(TIMEDIFF(datetime_on,datetime_off)), 24), ':',
	   MINUTE(TIMEDIFF(datetime_on, datetime_off)), ':',
	   SECOND(TIMEDIFF(datetime_on, datetime_off)), '')
	   AS TimeDiff
	   from transaction t inner join appliance a on t.appliance_id=a.id inner join area ar on ar.id=a.area_id order by t.datetime_on"""
	rows= conn.execute(query)
	#rows = cursor.fetchall()
	server_list = []
	for row in rows:
		
			json = collections.OrderedDict()
			json["datetime_on"] = str(row[0])
			json["datetime_off"] = str(row[1])
			json["expense"] = row[2]
			json["appliance_name"] = row[3]
			json["area_name"] = row[4]
			json["duration"] = str(row[5])
		
			server_list.append(json)
			
	conn.close()
	return JSON.dumps(server_list)
@app.route("/task_create", methods=['POST'])
def createTask():
  #  print("create")
  #  userRole = session.get('userRole')
   # userCodeRole = isRoleValid(userRole)
  #  if session.get('logged_in') != True or userCodeRole == False:
   #     print("if Session")
   #     print(session)
   #     return redirect(url_for('dashboard'))
    
    description=request.form['name']
    timeTask=request.form['time-task']
    action=request.form['action']
    area=request.form['area-id']
    global appliance_task
    appliance_task=request.form.get('appliance-id', type=int)
    
  
    conn = engine.connect()
    query="insert into task ( name , description ,create_date,time, status,task_type_id,area_id,appliance_id)  values (%s,%s,%s,%s,%s,%s,%s,%s)"    
    data= conn.execute(query,(action,description, time.strftime("%Y-%m-%d"),timeTask , 1,1,area,appliance_task))
    #conn.commit()

    conn.close()
    msg = collections.OrderedDict()
    if data != None:
    	print("creating task")
    	print(appliance_task)
    	msg['status'] = 1
    	msg['msg'] = "task successfully created"
    	time_lights_off=timeTask
    	
    	if action=="task_light_off":
    		task_lights_off=True
    		th2=threading.Thread(target=daemon3) #apagado
    		th2.daemon = True
    		th2.start()
    	else:
    		task_lights_on=True
    		th3=threading.Thread(target=daemon2) #encendido
    		th3.daemon = True
    		th3.start()
    else:
		msg = collections.OrderedDict()
		msg['status'] = 0
		msg['msg'] = "error, task not created"
    
    res = JSON.dumps(msg)
    return res

@app.route("/task_light_off", methods=['GET'])
def task_light_off():
	response="error"
	task_hour= request.args.get('task_hour')
	conn = engine.connect()
	query="insert into task ( name , description ,create_date,time, status,task_type_id)  values (%s,%s,%s,%s,%s,%s)"    
	data= conn.execute(query,("task_light_off","tarea apagar luz", time.strftime("%Y-%m-%d"),task_hour , 1,1))
	#conn.commit()
	conn.close()
	if data !=None:
		response="success"
		task_lights_off=True
		time_lights_off=task_hour
		
		th=threading.Thread(target=daemon3)
		th.daemon = True
		th.start()
	
	return response
@app.route("/arduino/temperature", methods=['GET'])
def getTemperatura():
	json = collections.OrderedDict()
	obj = collections.OrderedDict()
	msg='success'
	status=0	
	ser_data=""
	temperatura="0"
	try:
		ser.write("TEMPERATURA")
		time.sleep(1)
		ser_data=ser.readline()
		status=1
		if len(ser_data) == 0 or ser_data.strip().isdigit()==False:
			msg="error temp serial"
		else:
			temperatura=ser_data
	except Exception as e:
		print(e)
		temperatura="0"
		msg="error temperature"

	json["status"] = status
	json["msg"] = msg
	obj['value'] = temperatura
	json["temperature"] = obj
	print("temp: "+temperatura)
	
 	return JSON.dumps(json)

@app.route("/arduino/humidity", methods=['GET'])
def getHumedad():
	json = collections.OrderedDict()
	obj = collections.OrderedDict()
	msg='success'
	status=0		
	ser.write("HUMEDAD")
	humedad=""
	try:
		ser_data=ser.readline()
		humedad=ser_data
		status=1
		if len(ser_data) == 0 or humedad.strip().isdigit()==False:
			humedad="0"
	except Exception as e:
		print(e)
		humedad="0"
		msg="error humidity"

	json["status"] = status
	json["msg"] = msg
	obj['value'] = humedad
	json["humidity"] = obj
	
	
 	return JSON.dumps(json)

@app.route("/arduino/alarm_status", methods=['GET'])
def getAlarmStatus():
	
	alarm_status="0"
	conn = engine.connect()
	rows=conn.execute("select status from sensor where id = 7 ")
	#rows = cursor.fetchall()
	conn.close()
	for row in rows:
		alarm_status=str(row[0])
	return alarm_status

@app.route("/arduino/alarm", methods=['GET'])
def arduinoAlarm():
	action = request.args.get('action')
	json = collections.OrderedDict()
	msg='success '+action
	status=1
	try:
		func, args  = {
		  'alarm_mov_on': (changeAlarmStatus,('ALARM_MOV_ON',1,7,)),
		  'alarm_gas_on': (changeAlarmStatus,('ALARM_GAS_ON',1,8,)),
		  'alarm_gas_off': (changeAlarmStatus,('ALARM_GAS_OFF',0,8,))
		}.get(action, (changeAlarmStatus,('ALARM_MOV_OFF',0,7,)))

		result = func(*args)
		ser=serial.Serial('/dev/ttyACM0',9600,timeout=2)
	except:
		print "serial not connected"
		msg='error'
		status=0

	if  action=='alarm_mov_on':
		daemon_alarm_actived=True
		th1=threading.Thread(target=daemon)
		th1.daemon = True
		th1.start()
		os.system('./texto_a_voz.sh '+ 'Alarma, activada')
	if  action=='alarm_gas_on':
		daemon_alarm_actived=True
		th1=threading.Thread(target=daemon)
		th1.daemon = True
		th1.start()
		os.system('./texto_a_voz.sh '+ 'Alarma, activada')
	json["status"] = status
	json["msg"] = msg
 	return jsonify(json)

@app.route("/arduino/lock", methods=['GET'])
def arduinoLock():
	action = request.args.get('action')
	json = collections.OrderedDict()
	msg='success '+action
	status=0
	try:
		print(action.upper())
		ser.write(str(action).strip().upper())
		time.sleep(1)
		ser_data=ser.readline()
		if len(ser_data)>0:
			status=1
	except:
		msg='error'
		status=0

	json["status"] = status
	json["msg"] = msg
	
	
 	return jsonify(json)
def daemon():
	
	while True:
		sensor_id=0
		ser_data=ser.readline()
		if  len(ser_data) > 0:
			if ser_data.strip() == "HAY MOVIMIENTO":
				sendTelegramMessage("🚨 Alerta ⚠, Posible Intruso detectado❗🔓🤔😬😨",1)
				sensor_id=7
			if ser_data.strip() == "FUGA_GAS":
				sendTelegramMessage("🚨 Alerta ⚠, Posible Fuga de Gas❗🔓🤔😬😨",2)
				sensor_i=8
			if sensor_id != 0:
				conn = engine.connect()
				conn.execute("""UPDATE sensor SET status=%s WHERE id = %s""", (0,sensor_id))
				#conn.commit()                           
				conn.close()
				sensor_id=0
				break

def daemon2():
	print("running task lights on")
	print(appliance_task)
	conn = engine.connect()
	query="select time from task where name=%s and appliance_id=%s and status =%s order by time desc limit 1"

	rows= conn.execute(query,('task_light_on',appliance_task,1))
	conn.close()
	#rows = cursor.fetchall()
	light_status="off"
	task_lights_on=False
	for row in rows:
			task_lights_on=True
			time_lights_on = row[0]
			print("entra")
	while True:
		if task_lights_on:
			current_time = getCurrentTime()
			if light_status=="off":
				print(current_time)
				print(time_lights_on)
			if time_lights_on[0:5]==current_time and light_status=="off":
				ser.write("LIGHT_ON_L1")
				time.sleep(1)
				print("LIGHT_ON_L1")
				conn = engine.connect()
				conn.execute("""UPDATE task SET status=%s WHERE appliance_id = %s""", (0,appliance_task))
				#conn.commit()                           
				conn.close()
				light_status="on"
				break
				
		
def daemon3():
	print("running task lights off")
	conn = engine.connect()
	query="select time from task where name=%s and appliance_id=%s and status=%s limit 1"

	rows= conn.execute(query,('task_light_off',appliance_task,1))
	conn.close()
	#rows = cursor.fetchall()
	light_status="on"
	for row in rows:
			task_lights_off=True
			time_lights_off = row[0]
			print(time_lights_off)
	while True:
		if task_lights_off:
			current_time = getCurrentTime()
			if light_status=="on":
				print(current_time)
				print(time_lights_off)
			if time_lights_off[0:5]==current_time and light_status=="on":
				ser.write("LIGHT_OFF_L1")
				print("LIGHT_OFF_L1")
				conn = engine.connect()
				conn.execute("""UPDATE task SET status=%s WHERE appliance_id = %s""", (0,appliance_task))
				#conn.commit()                           
				conn.close()
				light_status="off"
				break

def sendWhatsappMessage(msg):
	print("enviando Whatsapp")
	os.system("yowsup-cli demos -l 595992871584:AKpAWiC0CE48/dMw9WUCFhaCDqY=  -s 595985991956 '"+msg+"'")

def sendTelegramMessage(mensaje,alert_type):
	if alert_type==1:
		camera.start_preview()
	  	time.sleep(1)
	  	camera.capture('/home/pi/intruso.jpg')
	  	camera.stop_preview()
		subprocess.call(["./tg.sh", "Domo_home", mensaje])
	else:
		subprocess.call(["./tg2.sh", "Domo_home", mensaje])
	


def changeAlarmStatus(alarm_type,alarm_status,sensor_id):
	ser.write(alarm_type)
	
	print(alarm_type)
	conn = engine.connect()
	conn.execute("""UPDATE sensor SET status=%s WHERE id = %s""", (alarm_status,sensor_id))
	#conn.commit()                           
	conn.close()

def getCurrentTime():
	timenow= time.time() - 60*60 
	#m2=time.strftime("%I:%M") 
	currenttime =time.strftime("%I:%M",time.localtime(timenow))
	#currenttime =time.strftime("%I:%M")
	return currenttime
	#if currenttime >= "10:00" and currenttime <= "13:00":
	 #   if m2 >= "10:00" and m2 >= "12:00":
	 #       m2 = ("""%s%s""" % (m2, " AM"))
	  #  else:
	   #     m2 = ("""%s%s""" % (m2, " PM"))
	#else:
	 #   m2 = ("""%s%s""" % (m2, " PM"))
	##m2 = datetime.datetime.strptime(m2, '%I:%M %p')
	#m2 = m2.strftime("%H:%M %p")
	#m2 = m2[:-3]
	#return m2

@app.route("/voiceCommand", methods=['POST'])
def voiceCommand():
	json = collections.OrderedDict()
	voz=request.form['voice']
	pro=request.form['pid']
	print(voz)
	if voz:	
		music = None
		ser.write("TEMPERATURA")
		time.sleep(1)
		ser_data=ser.readline()
		status=1
		if voz == "temperatura":
			if len(ser_data) == 0 or ser_data.strip().isdigit()==False:
				os.system('./texto_a_voz.sh '+ ' Temperatura no disponible')
			else:
				temperatura=ser_data
			  	os.system('./texto_a_voz.sh  Temperatura, '+str(ser_data).strip()+' grados')	
	        	#os.system('./texto_a_voz.sh  grados')	  
      		
		if voz == "hola":
		   os.system('./texto_a_voz.sh  Hola, que tal')
                   
		if  voz == "activar alarma":
		    os.system('./texto_a_voz.sh  Alarma, activada')
		    

		if  voz == "quien sos":
		    os.system('./texto_a_voz.sh  Hola, soy el sistema domótico!')
		    
		if  voz == "musica":
			os.system('./texto_a_voz.sh  Que empiece la fiesta!')
			music = Popen('mpg321 /usr/local/domotica/domotica_web_client/happy.mp3', stdout=subprocess.PIPE, 
                       shell=True, preexec_fn=os.setsid)
			pro = music.pid
			#music = os.popen('mpg321 /usr/local/domotica/domotica_web_client/happy.mp3', 'w')
		if  voz == "parar musica":
			os.killpg(os.getpgid(int(pro)), signal.SIGTERM) 

		if voz == "luces":
				ser.write("LIGHT_ON_L1")
				time.sleep(2)
				ser.write("LIGHT_ON_L2")
				time.sleep(1)
		if voz == "apagar luces":
				ser.write("LIGHT_OFF_L1")
				time.sleep(2)
				ser.write("LIGHT_OFF_L2")
				time.sleep(1)			 

	json["status"] = 1
	json["pid"] = pro
	json["msg"] = "ok"
	return JSON.dumps(json)
@app.route("/task_list")
def task_list():
    userRole = session.get('userRole')
    validRole = isRoleValid(userRole)
    conn = engine.connect()
    query = "select t.id, t.name, t.description, t.create_date, t.time, t.status, t.task_type_id, a.name, app.name from task t inner join area a on t.area_id = a.id inner join appliance app on t.appliance_id = app.id"
    #"select t.id, t.name, t.description, t.create_date, t.time, t.status, t.task_type_id, a.name, app.name from task t inner join area a on t.area_id = a.id inner join appliance app on t.appliance_id = app.id;"

    rows=conn.execute(query)
    conn.close()
    #rows = cursor.fetchall()
 
    task_list = []
    for row in rows:
        d = collections.OrderedDict()
        d['id'] = row[0]
        # d['name'] = row[1]
        d['description'] = row[2]
        d['creationDate'] = str(row[3])
        d['time'] = str(row[4]) 
        d['status'] = row[5]
        d['area'] = row[7]
        d['appliance'] = row[8]
        d['validRole'] = validRole
        task_list.append(d)
    #cursor.close()

    if rows != None:
        return JSON.dumps(task_list)
    # else:
    #     msg = collections.OrderedDict()
    #     msg['status'] = 0
    #     msg['msg'] = "Error, no se pudo obtener la lista de tareas"
    #     return JSON.dumps(msg)
	
@app.route("/task_edit", methods=['POST'])
def task_edit():
    userRole = session.get('userRole')
    userCodeRole = isRoleValid(userRole)
    if session.get('logged_in') != True or userCodeRole == False:
        print("if Session")
        print(session)
        return redirect(url_for('dashboard'))

    id=request.form['id']
    status=request.form['status']
    
    print(id)

    conn = engine.connect()
    data = conn.execute("""UPDATE task SET status=%s WHERE id=%s""", (status, id))
    
    #conn.commit()
    conn.close()
    print(data)
    msg = collections.OrderedDict()
    if data != None:
        msg['status'] = 1
        msg['msg'] = "Se cambió correctamente el estado de la tarea."
    else:
        msg = collections.OrderedDict()
        msg['status'] = 0
        msg['msg'] = "No se pudo cambiar el estado de la tarea."
    
    res = JSON.dumps(msg)
    return res
@app.route("/get_active_appliances_by_areaid")
def getActiveAppliancesByAreaId():
    areaId = request.args.get('areaId')
    conn = engine.connect()
    queryAppliance="select * from appliance where status = '{activo}' and area_id = '{areaId}'".format(activo=1,areaId=areaId)
    appliance_list = []
    appliance_rows=conn.execute(queryAppliance)
    #appliance_rows=cursor.fetchall()

    for row in appliance_rows:
        appliance = collections.OrderedDict()
        appliance['id'] = row[0]
        appliance['name'] = row[1]
        # appliance['power'] = row[2]
        # appliance['description'] = str(row[3])
        # appliance['fee'] =  row[4 ]
        # appliance['status'] =  row[5]
        appliance_list.append(appliance)
    conn.close()
    print(appliance_list)
    if len(appliance_list) > 0 and appliance_list != None:
        return JSON.dumps(appliance_list)
    else:
        print("error")
def getSerialData():
		try:
			if ser.is_open == 0:	
				ser.open()
			incoming = ser.readline()
			ser.close()
			return incoming
		except serial.serialutil.SerialException:
			print("No serial data this time")
			ser.close()
			return ''

def getSerialConnection():
		while (ser.inWaiting()>0):
			try:
				incoming = ser.readline()
				return incoming
			except serial.serialutil.SerialException:
				print("No data this time")
				return ''
	
if __name__ == "__main__":
    app.run(host='0.0.0.0',threaded=True)
