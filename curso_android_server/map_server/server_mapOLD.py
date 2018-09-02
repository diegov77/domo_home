# Coding: latin1
from __future__ import generators 
import cgi
from flask_cors import CORS, cross_origin
from flask import request
from flask import jsonify
import json as JSON
import collections
import datetime as datetime
from flask import Flask, render_template, session
#from flask_socketio import send, emit
import psycopg2
import sys
import time as time
from flask_session import Session
import hashlib
import jinja2
from flask import g
import jsonh
import facebook
import sqlalchemy.pool as pool
from sqlalchemy import create_engine
#from sqlalchemy.pool import QueuePool
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)


application = Flask(__name__)
application.secret_key = "987321654011"
application.config['SESSION_TYPE'] = 'filesystem'
application.config['SECRET_KEY'] = '987321654011'
application.config.from_object(__name__)
Session(application)
cors = CORS(application, resources={r"/*": {"origins": "*"}})

api_path ="/api/v1/"
global conn
global mypool
reload(sys)
sys.setdefaultencoding("utf-8")

db_dev = '192.168.1.111'
db_prod = 'fhacktions-virginia-m4-xlarge.c5cobzjg6fm8.us-east-1.rds.amazonaws.com'

def getconn():
	try:
		con = psycopg2.connect("dbname='smartfox_db' user='smartf' host='" + db_prod + "' password='miniP4ssPostgres'")
		con.autocommit = True
		return con
	except Exception as e:
		print "can't connect to  database"
		print(e)
		return 
mypool = pool.QueuePool(getconn,max_overflow=10, pool_size=5)

#conn = getconn()

#def testConnection():
#	global conn
#	con = getattr(g, '_database', conn)
#	if con.closed:
#		print('closed')
#		conn = openDbConnection()
#	return
def ResultIter(cursor, arraysize=1000): #fetching optimization of data
     while True:
        results = cursor.fetchmany(arraysize)
        if not results:
            break
        for result in results:
            yield result
@application.route("/logout")
def logout():
	session['logged_in'] = False

	
	return  render_template ("login.html",time=time) 

@application.route("/admin")
def mapAdmin():
		

		if session.get('logged_in') == True:
			return  render_template ("map_admin.html",time=time)
		else:
			return  render_template ("login.html",time=time)
		
@application.route("/login",methods=['GET','POST'])
def login():
	 if request.method == 'POST':
		user=request.form['user']
		password=request.form['pass']
		
		if user=='map_admin' and password=='tecHam82.':
			
			session['logged_in'] = True
			return  "success"
		else:
			return 'invalid user or password'
	 else:	
	 	return render_template ("login.html",time=time)		
@application.route("/")
def userIndex():
		

		return render_template ("map.html",time=time)
	

@application.route(api_path+"serversHacked")
def serversHacked():
	country_code = request.args.get('countryCode')
	objson = collections.OrderedDict()
	if country_code == None or country_code == '':
		return "bad request"
	rows=[]
	query=""
	if country_code=='PY':
		query="""SELECT serv_x,serv_y,serv_nombre,f.facc_nombre,u.usua_usuario,u.usua_email,serv_premium,s.serv_id,s.serv_owner,f.facc_activo,s.sety_id from servidores as s left join facciones as f on s.serv_hacked_faccion=f.facc_id 
		left join usuarios as u on s.serv_hacked_user = u.usua_id 
		where (f.facc_id!=998 or f.facc_id is null)  and (serv_y between -85.078125  and  -33.750000) 
		and (serv_x between -56.806893 and 15.527791 ) and serv_active = true
		order by f.facc_nombre"""
	else:
		query="""SELECT serv_x,serv_y,serv_nombre,f.facc_nombre,u.usua_usuario,u.usua_email,serv_premium,s.serv_id,s.serv_owner,f.facc_activo,s.sety_id,serv_country from servidores as s left join facciones as f on s.serv_hacked_faccion=f.facc_id 
		left join usuarios as u on s.serv_hacked_user = u.usua_id 
		where (f.facc_id!=998 or f.facc_id is null) and serv_country='"""+country_code+"""' and serv_active = true
		order by f.facc_nombre """
	try:
		conn = mypool.connect()
		cur = conn.cursor()
		cur.execute(query)
		rows =ResultIter(cur)
	except Exception as e:
		print(e)
		print "connection error"
		return ""
	finally:
		conn.close()


	server_list = []
	features_list = []
	geoJson = collections.OrderedDict()
	geoJson['type'] = "FeatureCollection"
	is_login = False
	if session.get('logged_in') == True:
		is_login = True
	for row in rows:
			servers = collections.OrderedDict()
			
			#location = geolocator.reverse(str(row[0]) + " , " + str(row[1]))
			#location = geolocator.reverse("48.8588443, 2.2943506")

			#print(location.address)

			
			#features_list.append(geoFeaturesData)
			#features_list.append(geometryObj)
			
			
			#objects_list.append(servers)
			servers['lat'] = row[0]
			servers['lon'] = row[1]
			servers['name'] = row[2]
			servers['fhacktion'] = row[3]
			servers['user'] = row[4]
			servers['serv_premium'] = row[6]
			if is_login:
				servers['serv_id'] = row[7] 
			servers['serv_owner'] = row[8]
			servers['sety_id'] = row[10]
			server_list.append(servers)
    		

	#geoJson['features'] = features_list
		        
	geo_str = JSON.dumps(server_list)
	cur.close()

	
	return geo_str

@application.route(api_path+"premiumUnhacked",methods=['GET'])
def premiumUnhacked():
	rows=[]
	country_code = request.args.get('countryCode')
	if country_code == None or country_code == '':
		return "bad request"
 	objson = collections.OrderedDict()
	try:
		if country_code=='PY':
			query="""SELECT serv_x,serv_y,serv_nombre,serv_premium,serv_id from servidores 
				where  serv_premium = true and serv_hacked_faccion is null and serv_hacked_user is null and serv_active = true"""
		else:
			query="""SELECT serv_x,serv_y,serv_nombre,serv_premium,serv_id from servidores 
				where  serv_premium = true and serv_hacked_faccion is null and serv_country='"""+country_code+"""' and serv_hacked_user is null and serv_active = true"""
		conn = mypool.connect()
		cur = conn.cursor()
		cur.execute(query)
		rows=ResultIter(cur)
	except Exception as e:
		print(e)
		print "connection error"
		return ""
	finally:
		conn.close()

	
	server_list = []
	for row in rows:
			servers = collections.OrderedDict()
			servers['lat'] = row[0]
			servers['lon'] = row[1]
			servers['name'] = row[2]
			servers['serv_premium'] = row[3]
	
			server_list.append(servers)
    		
      
	geo_str = JSON.dumps(server_list)
	cur.close()
	
	
	return geo_str

@application.route(api_path+"serversNoHacked")
def serversNoHacked():
	rows=[]
	country_code = request.args.get('countryCode')
	if country_code == None or country_code == '':
		return "bad request"
	objson = collections.OrderedDict()
	try:
		conn = mypool.connect()
		cur = conn.cursor()
		if country_code=='PY':
			query="""SELECT serv_x,serv_y,SUBSTRING ( serv_nombre ,0 , 26 ),s.sety_id,s.serv_id,s.serv_owner,u.usua_usuario,f.facc_nombre,s.serv_premium from servidores as s left join facciones as f on s.serv_hacked_faccion=f.facc_id 
			left join usuarios as u on s.serv_hacked_user = u.usua_id 
			where f.facc_id=998  and  (serv_y between -85.078125  and  -33.750000) 
			and (serv_x between -56.806893 and 15.527791 ) and serv_active = true
			order by f.facc_nombre"""
		else:
			query="""SELECT serv_x,serv_y,SUBSTRING ( serv_nombre ,0 , 26 ),s.sety_id,s.serv_id,s.serv_owner,u.usua_usuario,f.facc_nombre,s.serv_premium from servidores as s left join facciones as f on s.serv_hacked_faccion=f.facc_id 
			left join usuarios as u on s.serv_hacked_user = u.usua_id 
			where f.facc_id=998  and  serv_active = true and serv_country='"""+country_code+"""' 
			order by f.facc_nombre"""

		cur.execute(query)
		rows=ResultIter(cur)
	except Exception as e:
		print(e)
		print "connection error"
		return ""
	finally:
		conn.close()

	is_login = False
	if session.get('logged_in') == True:
		is_login = True
	
	server_list = []
	for row in rows:
			servers = collections.OrderedDict()
			servers['a'] = row[0]
			servers['o'] = row[1]
			servers['n'] =row[2]
			servers['y'] =row[3]
			if is_login:
				servers['i'] = row[4]
				servers['w'] = row[5]
				servers['u'] =row[6]
				servers['f'] =row[7]
				servers['p'] =row[8]
			
			

			server_list.append(servers)
	cur.close()	
      
	dumped = jsonh.dumps(server_list)
	
	
	return dumped


@application.route(api_path+"bestFhacktions")
def bestFhacktions():
	try:
		conn = mypool.connect()
		cur = conn.cursor()
		cur.execute("""select s.serv_hacked_faccion as facc_id, max(f.facc_nombre) as server_name, count(s.serv_nombre) as servers_count,facc_nivel
		from servidores s
		join facciones f on f.facc_id = s.serv_hacked_faccion
		where s.serv_hacked_faccion is not null and serv_active = true and f.facc_id!=998 and f.facc_id != 1086
		group by s.serv_hacked_faccion,facc_nivel order by servers_count desc limit 20""")
	except:
		print "connection error"
		return ""
	finally:
		conn.close()
	

	rows = cur.fetchall()
	
	
	server_list = []
	for row in rows:
			servers = collections.OrderedDict()
			#servers['facc_id'] = row[0]
			servers['server_name'] = row[1]
			servers['servers_count'] = row[2]
			servers['facc_nivel'] = row[3]
			 

			server_list.append(servers)
	cur.close()
	return JSON.dumps(server_list)



@application.route(api_path+"premiumHackedInfo")
def premiumHackedInfo():
	try:
		conn = mypool.connect()
		cur = conn.cursor()
		cur.execute("""select s.serv_hacked_faccion as facc_id, max(f.facc_nombre) as facc_name, count(s.serv_nombre) as serv_name
			from servidores s
			join facciones f on f.facc_id = s.serv_hacked_faccion
			where s.serv_hacked_faccion is not null
			and s.serv_premium = true and serv_active = true
			group by s.serv_hacked_faccion
			order by serv_name desc """)
	except:
		print "connection error"
		return
	finally:
		conn.close()

	row_premium = cur.fetchall()
	premium_list = []
	for row in row_premium:
			servers_premium = collections.OrderedDict()
			
			#servers_premium['facc_id'] = row[0]
			servers_premium['facc_name'] = row[1]
			servers_premium['serv_name'] = row[2]
			premium_list.append(servers_premium)
	
	cur.close()
	return JSON.dumps(premium_list)


@application.route(api_path+"bestHackers")
def bestHackers():
	try:
		conn = mypool.connect()
		cur = conn.cursor()
		cur.execute("""select u.usua_usuario, sum(avat_xp) AS sum_exp
		from avatares a inner join usuarios u on a.usua_id=u.usua_id
		where avat_xp > 0 
		group by u.usua_usuario 
		order  by sum_exp desc limit 20""")
	except:
		print "connection error"
		return ""
	finally:
		conn.close()

	row_premium = cur.fetchall()
	premium_list = []
	for row in row_premium:
			servers_premium = collections.OrderedDict()
			
			#servers_premium['facc_id'] = row[0]
			servers_premium['user_name'] = row[0]
			servers_premium['avat_xp'] = str(row[1])
			premium_list.append(servers_premium)
	
	cur.close()
	return JSON.dumps(premium_list)

@application.route(api_path+"resetPass",methods=['GET','POST'])
def resetPass():

	json = collections.OrderedDict()
	uspr_token=""
	password=""
	usua_id=0

	if request.method == 'POST':
		pass1=request.form['newpass1']
		pass2=request.form['newpass2']
		password=pass1
		uspr_token = request.form['code']
		uspr_token=jinja2.escape(uspr_token)
		if 	pass1!=pass2:
			json['status'] = "password does not match"
			conn.close()
			return jsonify(json)
	else:
		uspr_token=request.args.get('code')
		uspr_token=jinja2.escape(uspr_token)
	
	try:
		conn = mypool.connect()
		cur = conn.cursor()
		query="SELECT usua_id as  id_usuario, uspr_token as token,EXTRACT(EPOCH FROM (now() - uspr_expiration))/60 as minutes from usuario_pass_reset where uspr_token =  '{uspr_token}' and  enable =  '{enable}' ".format(uspr_token=uspr_token,enable=1)
		cur.execute(query)
		rows=cur.fetchall()
	
		for row in rows:
			 
			usua_id =  row[0]
			    #json['token'] = row[1]
			if float(row[2])<60.0:

				json['status'] = "ok"
				
			else:
				json['status'] = "time expired"
				
				return jsonify(json)
		
		if len(json)==0:
				json['status'] = "token does not exist"
				
				return jsonify(json)

		if request.method == 'GET':
				
				return jsonify(json)
		if request.method == 'POST':
			
				h=hashlib.md5(password.encode())
				
				try:
					cur.execute("UPDATE usuarios SET usua_pass=(%s) WHERE usua_id = (%s)", (h.hexdigest(),usua_id ,))
					conn.commit()                         
					cur.close()
					cur = conn.cursor()
					cur.execute("UPDATE usuario_pass_reset SET enable=(%s) WHERE usua_id = (%s) and uspr_token=(%s)", ('false',usua_id,uspr_token ,))
					conn.commit()
					cur.close()
					
					json['status'] = "password updated"
					
					return jsonify(json)
				except Exception as e:
					print(e)
					json['status'] =  "error updating password"
					
					return jsonify(json)
	except:
		print "connection error"
		return ""
	finally:
		conn.close()

	json['status'] = "error"
	
	return jsonify(json)		
	
@application.route(api_path+"serversSize")
def serversSize():
	try:
		conn = mypool.connect()
		cur = conn.cursor()
		cursor.execute("""select s.serv_nombre,t.sety_description,s.serv_x,s.serv_y,s.serv_premium from servidores s left join server_types t on s.sety_id=t.sety_id
		where (serv_x between 58.257813 and 71.400391) and (serv_y between   17.094535 and 36.671875  ) and s.serv_active = true
		group by s.serv_nombre ,t.sety_description, s.serv_x,s.serv_y,s.serv_premium""")
	except:
		print "connection error"
		return ""
	finally:
		conn.close()


	rows = cursor.fetchall()
	server_list = []
	
	for row in rows:
			servers_group = collections.OrderedDict()
			
			
			servers_group['name'] = row[0]
			servers_group['group_name'] = row[1]
			servers_group['lat'] = row[2]
			servers_group['lon'] = row[3]
			servers_group['premium'] = row[4]
			server_list.append(servers_group)
			
	cursor.close()
	return JSON.dumps(server_list)


 #E-COOMMERCE API  
@application.route(api_path+"insertPurchase", methods=['POST'])
def processPurchase():
	token= None
	product_json=request.form['product_data']
	transaction_id = request.form['transaction_id']
	transaction_id = jinja2.escape(transaction_id)
	user_id=request.form['user_id']
	user_id=jinja2.escape(user_id)
	try:
		token = request.headers['Authorization']
		
	except Exception as e:
		print(e)
		return "access denied"

	vtoken=verify_auth_token(token)

	if vtoken=="ok":
		try:
			conn = mypool.connect()
			cursor = conn.cursor()

			try:
				products=JSON.loads(product_json)
				c=1;
				for item in products:
					
					product_id=item['product_id']
					product_id=jinja2.escape(product_id)

					lat=item['latitude']
					lat=jinja2.escape(lat)

					lon=item['longitude']
					lon=jinja2.escape(lon)

					server_name=item['server_name']
					server_name=jinja2.escape(server_name)
					
					json_receipt = collections.OrderedDict()
					json_receipt['Store']='WebStore'
					json_receipt['ProductId']=product_id
					json_receipt['TransactionID']=transaction_id+str(c)
					c=c+1
					query="select stpr_id from store_premium where stpr_web_id='{product_id}'".format(product_id=product_id)
					cursor.execute(query)
					rows=cursor.fetchall()
					if  len(rows)==0:
						cursor.close()
						return '{"status": "error product_id does not exists"}'
					for row in rows:
						store_id=row[0]

					query="select usua_platform from usuarios where usua_id='{user_id}'".format(user_id=user_id)
					cursor.execute(query)
					platform=cursor.fetchone()[0]
					if platform=="ios" and int(store_id)>6:
						product_id="ios."+product_id
					print(product_id)
					query="""select * from exchange_item(%s,%s,%s);"""
					
					cursor.execute(query, (user_id,product_id,JSON.dumps(json_receipt),))
					conn.commit()
					res=cursor.fetchone()[0]
					
					if res==228: # TRANSACTION_ALREADY_PROCESSED.
							cursor.close()
							print(res)
							return '{"status": "error transaction already processed"}'
					if res < 0: # The item couldn't be found. UNKNOW_ERROR
							cursor.close()
							return '{"status": "item not found"}'
					
					if int(store_id)>6: #is a server product
						

						query="select upse_id from user_purchased_servers where usua_id={user_id} and stpr_id={store_id}".format(user_id=user_id,store_id=store_id)
						cursor.execute(query)
						
						res2=cursor.fetchone()
						if  res2==0:
							 cursor.close()
							 return '{"status": "error deploying server"}'
						upse_id=res2[0]
						query="select * from deploy_purchased_server(%s,%s,%s,%s,%s,%s)" #deploy server
						lat=lat.replace(",", ".")
						lon=lon.replace(",", ".")
						cursor.execute(query,(user_id,upse_id,server_name,float(lat),float(lon),True))
						conn.commit()
						res=cursor.fetchone()[0]

						if res!=100: # TRANSACTION_ALREADY_PROCESSED.
							cursor.close()
							return '{"status": "server already deployed"}'

			except Exception as e:
				print(e)
				cursor.close()	
				return '{"status": "error inserting purchase"}'
		except:
			print "connection error"
			return ""
		finally:
			conn.close()
		cursor.close()
		

	else:
		return vtoken
	return '{"status": "ok"}'
	


@application.route(api_path+"createUser", methods=['POST'])
def createUser():
	user=request.form['user']
	user=jinja2.escape(user)

	password=request.form['password']
	h=hashlib.md5(password.encode())

	name=request.form['name']
	name=jinja2.escape(name)

	last_name=request.form['last_name']
	last_name=jinja2.escape(last_name)

	email=request.form['email']
	email=jinja2.escape(email)


	json = collections.OrderedDict()

	try:
		conn = mypool.connect()
		cursor = conn.cursor()
	
		data= cursor.execute("select usua_usuario from usuarios where usua_usuario = '{user}'".format(user=user))
		
		if  len(cursor.fetchall())>0:
			json['status']='user already exists'
		else:
			query="""INSERT INTO usuarios(
		             usua_usuario, usua_pass, usua_email, usua_edad, usua_nombre, 
		            usua_apellido, facc_id, usua_virt_coins, usua_nivel, usua_active, 
		            usua_image, usua_facebook_id, usua_uuid, usua_push_token, usua_platform, 
		            usua_last_location, usua_last_location_timestamp, usua_creation_timestamp, 
		            usua_rooted, usua_push_notification, usua_push_sound, usua_facction_join, 
		            usua_last_login, usua_last_device_uuid, usro_id, usua_language, 
		            usua_timezone, usua_country, usua_tutorial, usua_xp)
		    VALUES ( %s, %s, %s, %s, %s, %s, %s,%s,%s , %s, %s, %s,%s,%s,%s,%s,%s,%s,  %s, %s,%s,%s, %s,%s, %s, %s,  %s,%s, %s, %s) RETURNING usua_id;"""
			try:
				data= cursor.execute(query,( user,h.hexdigest() , email, None, name,last_name, None,3000, 1, 'Y','', None,None,None,'web',None,None,'now()',False, True,True,'now()','now()',None, 1, None,None,None, '{"map": false, "battle": false, "market": false, "avatars": false, "activeGuide": 1}', 0))
				conn.commit()
				json['status']='ok'
				json['user_id']= cursor.fetchone()[0]
			except:		
				cursor.close()
				json['status']='error creating user'
		cursor.close()
	except:
		print "connection error"
		return ""
	finally:
		conn.close()

	return jsonify(json)

@application.route(api_path+"Login", methods=['POST'])
def Login():
	user=request.form['user']
	user=jinja2.escape(user)

	password=request.form['password']
	h=hashlib.md5(password.encode())

	json = collections.OrderedDict()
	try:
		conn = mypool.connect()
		cursor = conn.cursor()
		data= cursor.execute("select usua_id from usuarios where usua_usuario = '{user}' and usua_pass='{password}'".format(user=user,password=h.hexdigest()))
	except:
		print "connection error"
		return ""
	finally:
		conn.close()

	rows=cursor.fetchall()
	if  len(rows)>0:
		json['status']='ok'
		json['id']=rows[0][0]
	else:
		json['status']='login failure'
	
	return jsonify(json) 

@application.route(api_path+"LoginFacebook", methods=['POST'])
def LoginFacebook():
	access_token=request.form['facebook_token']

	json = collections.OrderedDict()
	try:
		graph = facebook.GraphAPI(access_token)
		profile = graph.get_object('me')
		args = {'fields' : 'id,name,email', }
		profile = graph.get_object('me', **args)
		
		facebook_id=profile.get('id')
		facebook_name=profile.get('name')
		facebook_email=profile.get('email')

		conn = mypool.connect()
		cursor = conn.cursor()

		cursor.execute("select usua_id from usuarios where usua_facebook_id = '{facebook_id}' ".format(facebook_id=facebook_id))
		rows=cursor.fetchall()
		if len(rows)==0:
			query="""INSERT INTO usuarios(
	             usua_usuario, usua_pass, usua_email, usua_edad, usua_nombre, 
	            usua_apellido, facc_id, usua_virt_coins, usua_nivel, usua_active, 
	            usua_image, usua_facebook_id, usua_uuid, usua_push_token, usua_platform, 
	            usua_last_location, usua_last_location_timestamp, usua_creation_timestamp, 
	            usua_rooted, usua_push_notification, usua_push_sound, usua_facction_join, 
	            usua_last_login, usua_last_device_uuid, usro_id, usua_language, 
	            usua_timezone, usua_country, usua_tutorial, usua_xp)
	   		 VALUES ( %s, %s, %s, %s, %s, %s, %s,%s,%s , %s, %s, %s,%s,%s,%s,%s,%s,%s,%s, %s,%s,%s, %s,%s, %s, %s,  %s,%s, %s, %s) RETURNING usua_id;"""
			try:
				data= cursor.execute(query,( facebook_name,None , facebook_email, None, facebook_name,None, None,3000, 1, 'Y','', facebook_id,None,None,'web',None,None,'now()',False, True,True,'now()','now()',None, 1, None,None,None, '{"map": false, "battle": false, "market": false, "avatars": false, "activeGuide": 1}', 0))
				conn.commit()
				
				json['user_id']= cursor.fetchone()[0]
				
			except:		
				json['status']='error creating user'
			
		else:
			for row in rows:
				json['user_id']= row[0]

		json['status']='ok'
		json['facebook_data']=profile
		
	except:		
		json['status']='login facebook error'
	finally:
		conn.close()
		cursor.close()

	return jsonify(json) 

@application.route(api_path+'token', methods=['POST'])
def get_auth_token():
	password=request.form['password']
	username=request.form['username']
	if verify_password(username,password):
		token = generate_auth_token(username)
		return jsonify({ 'token': token.decode('ascii') })

	return "Authentication Error"


def verify_password(username, password):
	
	h=hashlib.md5(password.encode())

	json = collections.OrderedDict()
	try:
		conn = mypool.connect()
		cursor = conn.cursor()
		data= cursor.execute("select usua_usuario from usuarios where usua_usuario = '{username}' and usua_pass='{password}' or usua_facebook_id='{username}'".format(username=username,password=h.hexdigest()))
	except:
		print "connection error"
		return ""
	finally:
		conn.close()

	if  len(cursor.fetchall())>0:
		cursor.close()

		return True
	else:
		cursor.close()
		return False

def generate_auth_token(username, expiration = 600):
    s = Serializer(application.config['SECRET_KEY'], expires_in = expiration) # 10min
    return s.dumps({ 'username': username })


def verify_auth_token(token):
    s = Serializer(application.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except SignatureExpired:
    	print(SignatureExpired)
        return "token Expired" # valid token, but expired
    except BadSignature:
    	print(BadSignature)
        return "Bad Signature" # invalid token
  
    
    return "ok"

@application.route(api_path+'productList', methods=['GET'])
def listProducts():
	token= None
	product_list = []
	try:
		token = request.headers['Authorization']
	except:
		return "access denied"

	vtoken=verify_auth_token(token)
	
	if vtoken=="ok":
		try:
			conn = mypool.connect()
			cursor = conn.cursor()
			cursor.execute("select stpr_web_id,stpr_description,stpr_price,stpr_name,stpr_image_path from store_premium where stpr_active=true")
		except:
			print "connection error"
			return ""
		finally:
			conn.close()
		rows=cursor.fetchall()
		
		for row in rows:
				json = collections.OrderedDict()
				json['product_id']=  row[0]
				json['description']=  row[1]
				json['price']=  row[2]
				json['name']=  row[3]
				json['image_path']=  row[4]
				
				product_list.append(json)
		cursor.close()
	else:
		return vtoken
	
	return jsonify(product_list)

@application.route("/productList")
def productList():


 
    objects_list = []
    c=1
    obj = collections.OrderedDict()
    for rows in range(0, 3):
        
                d = collections.OrderedDict()
                d['id'] = c
                d['name'] = "compresor " + str(c)
                d['description'] = "compresor industrial"
		d['image_path'] = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSXht91OuZm8g9UqUBjxGcQgxMlOIjnBiyfCfB7a2sWH8pAC-FZ9g"               
                d['price'] = 5000+c
                d['in_stock'] = 1;
		c = c + 1
            
                objects_list.append(d)
                obj['status'] = 'ok'
                obj['product_list']=objects_list
    j = JSON.dumps(obj)



    

    return j
@application.route("/product")
def product():
    prod_id = request.args.get('id')
    objects_list = []
    c=1
    obj = collections.OrderedDict()
    if prod_id != None and prod_id == '1':
        
        d = collections.OrderedDict()
        d['id'] = c
        d['name'] = "compresor " + str(c)
        d['description'] = "compresor industrial"
        d['image_path'] = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSXht91OuZm8g9UqUBjxGcQgxMlOIjnBiyfCfB7a2sWH8pAC-FZ9g"               
        d['price'] = 5000+c
        d['in_stock'] = 1;
        
       
        obj['status'] = 'ok'
        obj['product']=d

        
    else:
        obj['status'] = 'error el producto no existe'
    j = JSON.dumps(obj)

    return j


@application.route("/createProduct",methods=['POST'])
def createProduct():
    product_name=request.form['product_name']
    price=request.form['price']
    description=request.form['description']
    obj = collections.OrderedDict()

    if price != '' and description != '' and product_name != '':
        obj['status'] = 'ok'
        obj['msg'] = 'producto creado'
        print(product_name)
        print(price)
        print(description)
    else:
        obj['status'] = 'error'
        obj['msg'] = 'faltan datos'

    j = JSON.dumps(obj)


    return j


    return JSON.dumps(obj)

@application.route(api_path+"sendMessage",methods=['POST'])
def sendMessage():
    message=request.form['message']
   
    obj = collections.OrderedDict()

    if message!= None and message!='':
        obj['status'] = 'ok'
        obj['msg'] = 'mensaje recibido'
       

    else:
        obj['status'] = 'error'
        obj['msg'] = 'faltan datos'

    j = JSON.dumps(obj)


    return j



    return JSON.dumps(obj)


if __name__ == "__main__":
    application.run(host='0.0.0.0')
 
    
    
