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
import json
import collections
import datetime
from flask_cors import CORS, cross_origin
#from espeak import espeak
from flask import Flask, render_template
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})




@app.route("/productList")
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
    j = json.dumps(obj)



    

    return j
@app.route("/product")
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
        j = json.dumps(obj)



    return json.dumps(obj)

@app.route("/createProduct",methods=['POST'])
def resetPass():
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

    j = json.dumps(obj)


    return j

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
        print(message)

    else:
        obj['status'] = 'error'
        obj['msg'] = 'faltan datos'

    j = JSON.dumps(obj)


    return j


    return JSON.dumps(obj)

@application.route("/profiles")
def profiles():
 
    objects_list = []
    c=1
    obj = collections.OrderedDict()
    for rows in range(0, 5):

        d = collections.OrderedDict()
        d['id'] = c
        d['name'] = "name " + str(c)
        d['path_image'] = "https://www.ienglishstatus.com/wp-content/uploads/2018/04/Anonymous-Whatsapp-profile-picture.jpg"               
        d['created_date'] = "2018-05-12"

        c = c + 1
        objects_list.append(d)
    
    obj['status'] = 'ok'
    obj['profile_list']=objects_list
    j = JSON.dumps(obj)

   

    return j

@application.route("/profile", methods=['GET'])
def profile():
    id = request.args.get('id')
    objects_list = []
    c=1
    obj = collections.OrderedDict()
    if id != None and id == '1':

        d = collections.OrderedDict()
        d['id'] = c
        d['name'] = "name " + str(c)
        d['path_image'] = "https://www.ienglishstatus.com/wp-content/uploads/2018/04/Anonymous-Whatsapp-profile-picture.jpg"               
        d['created_date'] = "2018-05-12"

        c = c + 1
        obj['profile'] = d
    
    obj['status'] = 'ok'
    
    j = JSON.dumps(obj)

   

    return j


if __name__ == "__main__":
    app.run(host='0.0.0.0')
    
