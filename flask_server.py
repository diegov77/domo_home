# coding=utf-8
import cgi
import serial
import time
from flask import request
from flask import jsonify
import os
from flaskext.mysql import MySQL
import subprocess
import hashlib
import time
import json as JSON
import collections
import datetime
import sys
from flask_cors import CORS, cross_origin
#from espeak import espeak
from flask import Flask, render_template, session, redirect, url_for
from flask_session import Session
app = Flask(__name__)
app.secret_key = '987321654011'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = '987321654011'
app.config.from_object(__name__)
Session(app)
reload(sys)
sys.setdefaultencoding("utf-8")
cors = CORS(app, resources={r"/*": {"origins": "*"}})

mysql= MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1238'
app.config['MYSQL_DATABASE_DB'] = 'domo_home'
app.config['MYSQL_DATABASE_HOST'] = '192.168.1.54'
#app.config['MYSQL_DATABASE_HOST'] = '192.168.0.25'

mysql.init_app(app)
conn= mysql.connect()
cursor= conn.cursor()

#arguments = cgi.FieldStorage()
#Se queda como referencia, pero asi como esta no funciona.
@app.route("/session")
def SessionControl():
    print("algo")
    if session.get('logged_in') != True:
        print("if Session")
        return redirect(url_for('login'))#redirect("http://localhost:5000/login", code=302)

#VISTAS
@app.route("/")
def home():
    return render_template('dashboard.html')

@app.route("/login")
def login_get():
    print("login")
    if session.get('logged_in') == True:
        print("is logged")
        return redirect(url_for('userIndex'))
    return render_template('login.html')


@app.route("/login", methods=['POST'])
def login():
    if session.get('logged_in') == True:
        return redirect(url_for('userIndex'))
    
    cursor= conn.cursor()
    user=request.form['user']
    password=request.form['pass']
    h=hashlib.md5(password.encode())
    
    # query="select * from user where user = '{user}'  and password = '{password}'".format(user=user,password=h.hexdigest())
    query="select * from user u inner join role r on u.role_id = r.id where u.status = {activo} and u.user = '{user}' and u.password = '{password}'".format(activo=1,user=user,password=h.hexdigest())
    # query="select * from user u inner join role r on u.role_id = r.id where u.user = '{user}'".format(user=user)  #and u.password = '{password}'".format(user=user,password=h.hexdigest()) 
    
    result = cursor.execute(query)
    data=cursor.fetchall()
    print(data)
    userLogged = ""
    userRole = ""
    for row in data:
        userLogged = row[1]
        userRole = row[13]
    msg = collections.OrderedDict()
    cursor.close()
    print(result)
    if result:
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

def getActiveAreas():
    cursor= conn.cursor()
    queryArea="select * from area where status = '{activo}'".format(activo=1)
    area_list = []
    print(len(area_list))
    cursor.execute(queryArea)
    area_rows=cursor.fetchall()

    for row in area_rows:
        area = collections.OrderedDict()
        area['id'] = row[0]
        area['name'] = row[1]
        area['quantity'] = row[2]
        area['creation_date'] = str(row[3])
        area['status'] =  row[4 ]
        area['house_id'] =  row[5]
        area_list.append(area)
    cursor.close()
    print(len(area_list))
    if len(area_list) > 0 and area_list != None:
        return area_list
    else:
        area_list.append("No hay elementos.")
        return area_list

def getActiveAppliances():
    cursor= conn.cursor()
    queryAppliance="select * from appliance where status = '{activo}'".format(activo=1)
    appliance_list = []
    cursor.execute(queryAppliance)
    appliance_rows=cursor.fetchall()

    for row in appliance_rows:
        appliance = collections.OrderedDict()
        appliance['id'] = row[0]
        appliance['name'] = row[1]
        appliance['power'] = row[2]
        appliance['description'] = str(row[3])
        appliance['fee'] =  row[4 ]
        appliance['status'] =  row[5]
        appliance_list.append(appliance)
    cursor.close()
    if len(appliance_list) > 0 and appliance_list != None:
        return appliance_list
    else:
        appliance_list.append("No hay elementos.")
        return appliance_list

@app.route("/get_active_appliances_by_areaid")
def getActiveAppliancesByAreaId():
    areaId = request.args.get('areaId')
    cursor= conn.cursor()
    queryAppliance="select * from appliance where status = '{activo}' and area_id = '{areaId}'".format(activo=1,areaId=areaId)
    appliance_list = []
    cursor.execute(queryAppliance)
    appliance_rows=cursor.fetchall()

    for row in appliance_rows:
        appliance = collections.OrderedDict()
        appliance['id'] = row[0]
        appliance['name'] = row[1]
        # appliance['power'] = row[2]
        # appliance['description'] = str(row[3])
        # appliance['fee'] =  row[4 ]
        # appliance['status'] =  row[5]
        appliance_list.append(appliance)
    cursor.close()
    print(appliance_list)
    if len(appliance_list) > 0 and appliance_list != None:
        return JSON.dumps(appliance_list)
    else:
        print("error")

def getTemperature():
    temperatura = 22
    return temperatura 

def getHumidity():
    humedad = 60
    return humedad

def getCurrentExpense():
    consumoActual = 125000
    return consumoActual

def getAlarmStatus():
    alarmStatus = 0
    return alarmStatus

@app.route("/data_chart_area")
def getDataChartArea():
    area_expense_list = []
    area1 = collections.OrderedDict()
    area2 = collections.OrderedDict()

    area1['expense'] = 29.235999584197998
    area1['area_name'] = "cuarto1"
    area2['expense'] = 43.853999376297
    area2['area_name'] = "Sala"
    area_expense_list.append(area1)
    area_expense_list.append(area2)

    res = JSON.dumps(area_expense_list)
    return res

@app.route("/get_monthly_expense_by_area", methods=['GET'])
def get_monthly_expense_by_area():
    cursor= conn.cursor()
    month_num = request.args.get('month')
    if (month_num==None or month_num.strip()==""):
        #month_num="month(now())"
        month_num="0"
    json = collections.OrderedDict()
    

    query="select (TIMESTAMPDIFF(SECOND,datetime_on, datetime_off)/60/60)*power*fee as expense,ar.name as area_name from transaction t inner join appliance a on t.appliance_id=a.id inner join area ar on ar.id=a.area_id  where month(datetime_off)= "+month_num+" group by ar.name;"
    data= cursor.execute(query)
    rows = cursor.fetchall()
    server_list = []
    for row in rows:
        
            json = collections.OrderedDict()
            
            json["expense"] = row[0]
            json["area_name"] = row[1]
        
            server_list.append(json)
            
    cursor.close()
    return JSON.dumps(server_list)

@app.route("/get_monthly_expense_by_appliance", methods=['GET'])
def get_monthly_expense_by_appliance():
    cursor= conn.cursor()
    month_num = request.args.get('month')
    if (month_num==None or month_num.strip()==""):
        month_num="0"
    json = collections.OrderedDict()
    
    query="select (TIMESTAMPDIFF(SECOND,datetime_on, datetime_off)/60/60)*power*fee as expense,a.name as area_name from transaction t inner join appliance a on t.appliance_id=a.id where month(datetime_off)="+month_num+" group by a.name;"
    data= cursor.execute(query)
    rows = cursor.fetchall()
    server_list = []
    for row in rows:
        
        json = collections.OrderedDict()
        
        json["expense"] = row[0]
        json["appliance_name"] = row[1]
    
        server_list.append(json)
            
    cursor.close()
    return JSON.dumps(server_list)

@app.route("/get_monthly_expenses", methods=['GET'])
def get_monthly_expenses():
    cursor= conn.cursor()
    year = request.args.get('year')
    if year == None or year =="":
        year=2017
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
     from transaction  t inner join appliance a on t.appliance_id=a.id where EXTRACT(YEAR FROM datetime_off)=%s"""
    data= cursor.execute(query, year)
    rows = cursor.fetchall()
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

            
    cursor.close()
    return JSON.dumps(server_list)


@app.route("/get_all_expenses", methods=['GET'])
def get_all_expenses():
    print("llamada");
    cursor= conn.cursor()

    json = collections.OrderedDict()

    query="""select datetime_on,datetime_off, (TIMESTAMPDIFF(SECOND,datetime_on, datetime_off)/60/60)*power*fee as expense,a.name,ar.name,
        CONCAT( MOD(HOUR(TIMEDIFF(datetime_on,datetime_off)), 24), ':',
       MINUTE(TIMEDIFF(datetime_on, datetime_off)), ':',
       SECOND(TIMEDIFF(datetime_on, datetime_off)), '')
       AS TimeDiff
       from transaction t inner join appliance a on t.appliance_id=a.id inner join area ar on ar.id=a.area_id order by t.datetime_on"""
    data= cursor.execute(query)
    rows = cursor.fetchall()
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
            
    cursor.close()
    return JSON.dumps(server_list)

@app.route("/dashboard")
def dashboard():
    areaList = getActiveAreas()
    applianceList = getActiveAppliances()
    temperature = getTemperature()
    humidity = getHumidity()
    currentExpense = getCurrentExpense()
    alarmStatus = getAlarmStatus()
    areaExpense = getDataChartArea()
    areaExpenseList = jsonify(areaExpense)
    print(areaExpense)
    print(areaExpenseList)
    return render_template('dashboard.html',areas=areaList,appliances=applianceList,temperature=temperature,humidity=humidity,currentExpense=currentExpense,alarmStatus=alarmStatus,areaExpenseList=areaExpenseList,userLogged=session.get('userLogged'))

# @app.route("/get_total_expense", methods=['POST'])
# def getTotalExpense():
#     cursor= conn.cursor()
#     start_date = request.form['start_date']
#     end_date = request.form['end_date']
#     json = collections.OrderedDict()
#     print(end_date)
#     print(start_date)

    # query="select totalExpense('"+start_date+"','"+end_date+"')"
    # data= cursor.execute(query)
    # rows = cursor.fetchall()
    
    # for row in rows:
        # if data==1:
        #     json["status"] = 1
        #     json["result"] = row[0]
        # else:
        #     json["status"] = 'error'
        #     json["result"] = 0
    # json["status"] = 1
    # json["result"] = 'successful'
    # cursor.close()
    # return jsonify(json)

@app.route("/dashboard1")
def dashboard1():
    return render_template('dashboard_1.html')

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

@app.route("/task_list")
def getTask():
    userRole = session.get('userRole')
    validRole = isRoleValid(userRole)
    cursor = conn.cursor()
    query = "select t.id, t.name, t.description, t.create_date, t.time, t.status, t.task_type_id, a.name, app.name from task t inner join area a on t.area_id = a.id inner join appliance app on t.appliance_id = app.id"
    #"select t.id, t.name, t.description, t.create_date, t.time, t.status, t.task_type_id, a.name, app.name from task t inner join area a on t.area_id = a.id inner join appliance app on t.appliance_id = app.id;"

    cursor.execute(query)
    cursor.close()
    rows = cursor.fetchall()
 
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
    cursor.close()

    if rows != None:
        return JSON.dumps(task_list)
    # else:
    #     msg = collections.OrderedDict()
    #     msg['status'] = 0
    #     msg['msg'] = "Error, no se pudo obtener la lista de tareas"
    #     return JSON.dumps(msg)


@app.route("/task_create", methods=['POST'])
def createTask():
    print("create")
    userRole = session.get('userRole')
    userCodeRole = isRoleValid(userRole)
    if session.get('logged_in') != True or userCodeRole == False:
        print("if Session")
        print(session)
        return redirect(url_for('dashboard'))
    
    description=request.form['name']
    timeTask=request.form['time-task']
    action=request.form['action']
    area=request.form['area-id']
    appliance=request.form['appliance-id']
    
    
    task_name="task_light_on"
    if action=="0":
        task_name="task_light_off"


    
    cursor= conn.cursor()
    query="insert into task ( name , description ,create_date,time, status,task_type_id,area_id,appliance_id)  values (%s,%s,%s,%s,%s,%s,%s,%s)"    
    data= cursor.execute(query,(task_name,description, time.strftime("%Y-%m-%d"),timeTask , 1,1,area,appliance))
    conn.commit()
    cursor.close()
    msg = collections.OrderedDict()
    if data == 1:
        print("create task")
        msg['status'] = 1
        msg['msg'] = "task successfully created"
    else:
        msg = collections.OrderedDict()
        msg['status'] = 0
        msg['msg'] = "error, task not created"
    
    res = JSON.dumps(msg)
    return res

@app.route("/task_edit", methods=['POST'])
def editTask():
    userRole = session.get('userRole')
    userCodeRole = isRoleValid(userRole)
    if session.get('logged_in') != True or userCodeRole == False:
        print("if Session")
        print(session)
        return redirect(url_for('dashboard'))

    id=request.form['id']
    status=request.form['status']
    
    print(id)

    cursor = conn.cursor()
    data = cursor.execute("""UPDATE task SET status=%s WHERE id=%s""", (status, id))
    
    conn.commit()
    cursor.close()
    print(data)
    msg = collections.OrderedDict()
    if data == 1:
        msg['status'] = 1
        msg['msg'] = "Se cambió correctamente el estado de la tarea."
    else:
        msg = collections.OrderedDict()
        msg['status'] = 0
        msg['msg'] = "No se pudo cambiar el estado de la tarea."
    
    res = JSON.dumps(msg)
    return res

#================= End Section task services ===================

#Funcion para validar role admin y familia del usuario.
def isRoleValid(userRole):
    query = "select code from role where code = '{admin}' or code='{family}'".format(admin='A',family='F')
    cursor = conn.cursor()
    cursor.execute(query)
    codeRow = cursor.fetchall()
    role = False
    userCodeRole = ""
    for code in codeRow:
        if userRole == code[0]:
            role = True
            break
        # userCodeRole = code[0]

    cursor.close()
    return role
    # if userCodeRole == userRole:
    #     return True
    # else:
    #     return False

#Funcion para validar role admin del usuario.
def isRoleAdmin():
    userRole = session.get('userRole')
    query = "select code from role where code = '{admin}'".format(admin='A')
    cursor = conn.cursor()
    cursor.execute(query)
    codeRow = cursor.fetchall()
    print(codeRow)
    roleAdmin = ""
    for code in codeRow:
        roleAdmin = code[0]

    cursor.close()
    if roleAdmin == userRole:
        return True
    else:
        return False


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
    
    cursor = conn.cursor()
    query = "select * from user u inner join role r on r.id=u.role_id"

    cursor.execute(query)
    cursor.close()
    rows = cursor.fetchall()
 
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

    conn.commit()
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
    
    
    data= cursor.execute(query,(name,lastName,user,convertedPass,email,birthDate,creationDate,status,phone,roleId))
    #data=cursor.execute(query,("gabi","cabrera","gabi","123","fasdfa","2016-10-23","2016-01-02",1,"123456",1))
    conn.commit()
    #conn.close
    msg = collections.OrderedDict()
    if data == 1:
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
        
    cursor.execute(query)
    rows=cursor.fetchall()
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
    cursor = conn.cursor()
    session.get('userLogged')
    queryPass="select password from user where id = '{id}'".format(id=id)
    cursor.execute(queryPass)
    rowPass=cursor.fetchall()
    psw = ""
    for row in rowPass:
        psw = row[0]
    updatePass = password
    if psw != password:
        updatePass = convertedPass
    cursor.close()

    #query="insert user (id,name,lastname,user,password,mail,birth_date,creation_date,status,phone,role_id)  values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    cursor = conn.cursor()
    data = cursor.execute("""UPDATE user SET name=%s, lastname=%s, user=%s, password=%s, mail=%s, birth_date=%s, status=%s, phone=%s, role_id=%s WHERE id=%s""", (name, lastName, user, updatePass, email, birthDate, status, phone, roleId, id))
    
    
    #data= cursor.execute(query,(id,name,lastName,user,password,email,birthDate,status,phone,roleId))
    conn.commit()
    #conn.close
    msg = collections.OrderedDict()
    if data:
        
        
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
    cursor.execute(query)
    rows=cursor.fetchall()
    #print(row)

    for row in rows:
                area = collections.OrderedDict()
                area['id'] = row[0]
                area['name'] = row[1]
                area['quantity'] = row[2]
                area['creation_date'] = str(row[3])

                area['status'] =  row[4 ]
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
    
    data= cursor.execute(query,(name,creationDate,status,house_id))
    
    conn.commit()
    #conn.close
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

@app.route("/area_edit",methods=['GET'])
def areaEdit():
    userRole = session.get('userRole')
    userCodeRole = isRoleAdmin()
    if session.get('logged_in') != True or userCodeRole == False:
        return redirect(url_for('login'))

    area_id = request.args.get('areaId')
    d = collections.OrderedDict()
    
    query="select * from area a where a.id = '{id}'  ".format(id=area_id)
        
    cursor.execute(query)
    rows=cursor.fetchall()
    area = collections.OrderedDict()
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
    
    data = cursor.execute("""UPDATE area SET name=%s, status=%s WHERE id=%s""", (name, status, id))

    conn.commit()
    #conn.close
    
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
    cursor.execute(query)
    rows=cursor.fetchall()
    #print(row)

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

    cursor= conn.cursor()
    queryArea="select * from area"
    area_list = []
    cursor.execute(queryArea)
    area_rows=cursor.fetchall()

    for row in area_rows:
        area = collections.OrderedDict()
        area['id'] = row[0]
        area['name'] = row[1]
        area_list.append(area)
    cursor.close()

    cursor= conn.cursor()
    queryApplianceType="select * from appliance_type"
    appliance_type_list = []
    cursor.execute(queryApplianceType)
    appliance_type_rows=cursor.fetchall()

    for row in appliance_type_rows:
        appliance_type = collections.OrderedDict()
        appliance_type['id'] = row[0]
        appliance_type['name'] = row[1]
        appliance_type_list.append(appliance_type)
    cursor.close()

    cursor= conn.cursor()
    querySensor="select * from sensor"
    sensor_list = []
    cursor.execute(querySensor)
    sensor_rows=cursor.fetchall()

    for row in sensor_rows:
        sensor = collections.OrderedDict()
        sensor['id'] = row[0]
        sensor['name'] = row[1] + ", " + row[2]
        sensor_list.append(sensor)
    cursor.close()
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

    cursor = conn.cursor()
    query="insert into appliance (name,power,description,status,creation_date,sensor_id,area_id,appliance_type_id)  values (%s,%s,%s,%s,%s,%s,%s,%s)"
    data= cursor.execute(query,(name,power,description,status,creationDate,sensor_id,area_id,appliance_type_id))
    cursor.close()

    cursor = conn.cursor()
    queryApplianceQuantity = "select a.appliance_quantity from area a inner join appliance ap on a.id = ap.area_id where ap.area_id = '{id}'  ".format(id=area_id)
    print(queryApplianceQuantity)
    applianceQuantity = cursor.execute(queryApplianceQuantity)
    print(applianceQuantity)
    cursor.close()

    cursor = conn.cursor()
    newQuantity = applianceQuantity + 1
    print(newQuantity)
    dataUpdateArea = cursor.execute("""UPDATE area SET appliance_quantity=%s WHERE id=%s""", (newQuantity, area_id))    
    print(dataUpdateArea)
    conn.commit()
    cursor.close()
    #conn.close
        
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


@app.route("/appliance_edit",methods=['GET'])
def applianceEdit():
    userRole = session.get('userRole')
    userCodeRole = isRoleAdmin()
    if session.get('logged_in') != True or userCodeRole == False:
        return redirect(url_for('login'))

    appliance_id = request.args.get('applianceId')

    cursor= conn.cursor()
    query="select ap.id, ap.name, ap.power, ap.fee, ap.description, ap.status, ap.creation_date, s.id, a.id, apt.id from appliance ap inner join sensor s on ap.sensor_id=s.id inner join area a on ap.area_id=a.id inner join appliance_type apt on ap.appliance_type_id=apt.id where ap.id = '{id}'; ".format(id=appliance_id)
    cursor.execute(query)
    appliance_rows=cursor.fetchall()
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
    cursor.close()
    cursor= conn.cursor()
    queryArea="select * from area"
    area_list = []
    cursor.execute(queryArea)
    area_rows=cursor.fetchall()

    for row in area_rows:
        area = collections.OrderedDict()
        area['id'] = row[0]
        area['name'] = row[1]
        area_list.append(area)
    cursor.close()

    cursor= conn.cursor()
    queryApplianceType="select * from appliance_type"
    appliance_type_list = []
    cursor.execute(queryApplianceType)
    appliance_type_rows=cursor.fetchall()

    for row in appliance_type_rows:
        appliance_type = collections.OrderedDict()
        appliance_type['id'] = row[0]
        appliance_type['name'] = row[1]
        appliance_type_list.append(appliance_type)
    cursor.close()

    cursor= conn.cursor()
    querySensor="select * from sensor"
    sensor_list = []
    cursor.execute(querySensor)
    sensor_rows=cursor.fetchall()

    for row in sensor_rows:
        sensor = collections.OrderedDict()
        sensor['id'] = row[0]
        sensor['name'] = row[1] + ", " + row[2]
        sensor_list.append(sensor)
    cursor.close()
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
    cursor = conn.cursor()
    queryCurrentAreaId = "select ap.area_id from appliance ap where ap.id = '{id}' ".format(id=id)
    currentAreaId = 0
    cursor.execute(queryCurrentAreaId)
    currentArea_rows=cursor.fetchall()
    print(currentArea_rows)
    for row in currentArea_rows:
        currentAreaId = row[0]
    cursor.close()
    # print(currentAreaId)
    #updateAppQuantity = False
    
    cursor = conn.cursor()
    data = cursor.execute("""UPDATE appliance SET name=%s, power=%s, status=%s, description=%s, sensor_id=%s, area_id=%s, appliance_type_id=%s WHERE id=%s""", (name, power, status, description, sensor_id, area_id, appliance_type_id, id))
    cursor.close()
    # print(area_id)
    #Entra cuando no deberia
    if (str(currentAreaId) != area_id):

        #Obtener appliance quantity para sumar en areas.
        cursor = conn.cursor()
        queryApplianceQuantitySumar = "select a.appliance_quantity from area a inner join appliance ap on a.id = ap.area_id where ap.area_id = '{id}'  ".format(id=area_id)
        applianceQuantitySumar = 0
        cursor.execute(queryApplianceQuantitySumar)
        quantitySuma_rows=cursor.fetchall()
        for row in quantitySuma_rows:
            applianceQuantitySumar = row[0]
        print(applianceQuantitySumar)
        cursor.close()

        #Se actualiza el valor de appliance_quantity en area al que se agrega.
        cursor = conn.cursor()
        newQuantitySumar = applianceQuantitySumar + 1
        print("quantity suma: ")
        print(newQuantitySumar)
        dataUpdateAreaSuma = cursor.execute("""UPDATE area SET appliance_quantity=%s WHERE id=%s""", (newQuantitySumar, area_id))    
        print(dataUpdateAreaSuma)
        cursor.close()


        #Obtener appliance quantity para restar en areas.
        cursor = conn.cursor()
        queryApplianceQuantityRestar = "select a.appliance_quantity from area a inner join appliance ap on a.id = ap.area_id where ap.area_id = '{id}'  ".format(id=currentAreaId)
        applianceQuantityRestar = 0
        cursor.execute(queryApplianceQuantityRestar)
        quantityResta_rows=cursor.fetchall()
        for row in quantityResta_rows:
            applianceQuantityRestar = row[0]
        print(applianceQuantityRestar)
        cursor.close()

        #Se actualiza el valor de appliance_quantity en el area del que se quita.
        cursor = conn.cursor()
        newQuantityRestar = applianceQuantityRestar - 1
        print("quantity resta: ")
        print(newQuantityRestar)
        dataUpdateAreaResta = cursor.execute("""UPDATE area SET appliance_quantity=%s WHERE id=%s""", (newQuantityRestar, currentAreaId))    
        print(dataUpdateAreaResta)
    # conn.commit()
    cursor.close()

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


@app.route("/getTempVoice", methods=['POST'])
def temp():
	#voz = request.args.get('voz')
	voz=request.form['voz']
	if voz:	
		
		if voz == "temperatura":
		  os.system('./texto_a_voz.sh '+ 'temperatura 22 grados, humedad 65%')	
        	  return "voz received"
      		
		if voz == "Hola":
		   os.system('./texto_a_voz.sh '+ 'hola, que tal')
                   return "saludo"
		if  voz == "Activar alarma":
		    os.system('./texto_a_voz.sh '+ 'Alarma activada')
		    return "alarma activada"
	
 	else:
           return "welcome to tesis domotica"	  


@app.route("/temperatura")
def temperatura():
	os.system('./texto_a_voz.sh '+ 'temperatura 22 grados, humedad 65%')
        return 'temperatura'




	cursor.execute("""
            SELECT * from user
            """)

	rows = cursor.fetchall()
 
	objects_list = []
	for row in rows:
		 	d = collections.OrderedDict()
			d['id'] = row[0]
	    		d['name'] = row[1]
    			d['lastname'] = row[2]
    			d['user'] = row[3]
    		#	d['password'] = row[4]
    		
    			d['mail'] =  str(row[5]) #datetime.strftime("%Y-%m-%d %H:%M:%S")
    		#d['creation_date'] = row[6]
    			d['status'] = row[8]
    			d['phone'] = row[9]
    			d['role_id'] = row[9]
    		
			
	    		objects_list.append(d)
	j = JSON.dumps(objects_list)
	conn.commit()
	conn.close

	if rows != None:
	 return j
	else:
	 return "error al listar usuario"


	



@app.route("/getAreaList", methods=['GET'])
def getAreaList():
    
    cursor.execute("""
        SELECT * from area
        """)
            
    rows = cursor.fetchall()
    objects_list = []
    for row in rows:
            d = collections.OrderedDict()
            d['id'] = row[0]
            d['name'] = row[1]
            d['appliance_quantity'] = row[2]
            #d['creation_date'] = row[3]
            d['house_id'] = row[4]
                        
                        
                        
            objects_list.append(d)
    j = JSON.dumps(objects_list)
    conn.commit()
    conn.close
    if rows != None:
        return j
    else:
        return "error al listar area"


@app.route("/getUserList", methods=['GET'])
def getUserList():

	cursor.execute("""
            SELECT * from user
            """)

	rows = cursor.fetchall()
 
	objects_list = []
	for row in rows:
		 	d = collections.OrderedDict()
	                d['id'] = row[0]
	    		d['name'] = row[1]
    			d['lastname'] = row[2]
    			d['user'] = row[3]
    		#	d['password'] = row[4]
    		
    			d['mail'] =  str(row[5]) #datetime.strftime("%Y-%m-%d %H:%M:%S")
    		#d['creation_date'] = row[6]
    			d['status'] = row[8]
    			d['phone'] = row[9]
    			d['role_id'] = row[9]
    		
			
            #objects_list.append(d)
	                roll = collections.OrderedDict()
        	        roll['id'] = 1
                	roll['name'] = "admin"
               		d['role'] = roll
	                objects_list.append(d)
	j = JSON.dumps(objects_list)
	conn.commit()
	conn.close

	if rows != None:
	 return j
	else:
	 return "error al listar usuario"


	
@app.route("/getApplianceList", methods=['GET'])
def getApplianceList():

	cursor.execute("""
    	SELECT * from appliance
    	""")
        
        rows = cursor.fetchall()


    
	objects_list = []
        for row in rows:
                d = collections.OrderedDict()
                d['id'] = row[0]
                d['name'] = row[1]
                d['power'] = row[2]
                d['description'] = row[3]
                d['fee'] = row[4]
                d['status'] = row[5]
                #d['creation_date'] = row[6]
                d['sensor_id'] = row[7]
                d['area_id'] = row[8]
                d['appliance_type_id'] = row[9]
                
                
                objects_list.append(d)
    	j = JSON.dumps(objects_list)
        conn.commit()
        conn.close
        
        if rows != None:
            return j
        else:
            return "error al listar appliance"



if __name__ == "__main__":
    app.run(host='0.0.0.0')
    
