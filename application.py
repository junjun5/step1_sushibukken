from flask import Flask
from flask import render_template
from data.database import init_db
import os
from flask import redirect
from flask import request
from flask import url_for
from data.database import db
from models.user import User
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map

import pandas as pd

import pymysql


app = Flask(__name__,static_folder='./static')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:////tmp/test.db')
init_db(app)
# try:
#     conn = mysql.connector.connect(user='myadmin@mydemoserver',
#                                    password='yourpassword',
#                                    database='quickstartdb',
#                                    host='mydemoserver.mysql.database.azure.com',
#                                    ssl_ca='/var/www/html/BaltimoreCyberTrustRoot.crt.pem')
# except mysql.connector.Error as err:
    # print(err)

def getConnection():
    return pymysql.connect(
        host='yourdatabaseserver',
        db='yourdb',
        user='azuser',
        password='type your password',
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor,
        ssl={'ca': './BaltimoreCyberTrustRoot.crt.pem'}
    )
    # conn = pymysql.connect(user='myadmin@mydemoserver',
    #                    password='yourpassword',
    #                    database='quickstartdb',
    #                    host='mydemoserver.mysql.database.azure.com',
    #                    ssl={'ca': '/var/www/html/BaltimoreCyberTrustRoot.crt.pem'})

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/michelin")
def sushiRestaurant():
    connection = getConnection()
    sql1 = "SELECT * FROM sushi_shops limit 3"
    sql2 = "SELECT * FROM sushi_shops limit 3,3"

    cursor = connection.cursor()
    cursor.execute(sql1)
    restaurants = cursor.fetchall()
    cursor.execute(sql2)
    under_restaurants = cursor.fetchall()

    cursor.close()
    connection.close()
    return render_template('sushiRestaurant.html', restaurants=restaurants, under_restaurants=under_restaurants)
    
@app.route("/bukken")
def bukken():
    connection = getConnection()
    sql = "SELECT * FROM suumo_items limit 1,4"

    cursor = connection.cursor()
    cursor.execute(sql)
    bukkens = cursor.fetchall()

    cursor.close()
    connection.close()
    return render_template('bukken.html' , bukkens=bukkens )

@app.route("/image")
def image():
    return render_template('image.html')

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

@app.route('/sushishop', methods=['GET'])
def sushishop():
    connection = getConnection()
    sql = "SELECT * FROM sushi_shops"
    cursor = connection.cursor()
    cursor.execute(sql)
    restaurants = cursor.fetchall()

    cursor.close()
    connection.close()
    return render_template('restaurant/index.html', restaurants=restaurants)

@app.route('/suumoitems', methods=['GET'])
def suumoitems():
    connection = getConnection()
    sql = "SELECT * FROM suumo_items"
    cursor = connection.cursor()
    cursor.execute(sql)
    bukkens = cursor.fetchall()

    cursor.close()
    connection.close()
    return render_template('bukken/index.html', bukkens=bukkens)

@app.route('/users', methods=['GET'])
def users_index():

    connection = getConnection()

    sql = "SELECT * FROM user"
    cursor = connection.cursor()
    cursor.execute(sql)
    users = cursor.fetchall()

    cursor.close()
    connection.close()
    #users = User.query.order_by(User.id.desc()).all()
    # return render_template('users/index.html', users=users)
    return render_template('users/index.html', users=users)

@app.route('/users/details/<int:id>', methods=['GET'])
def users_details(id=0):
    user = User.query.get(id)
    return render_template('users/details.html', user=user)

@app.route('/users/create', methods=['GET'])
def users_create():
    return render_template('users/create.html')

@app.route('/users/create', methods=['POST'])
def users_create_post():

    connection = getConnection()

    sql = "INSERT INTO user (`username`)  VALUES (%s)"
    cursor = connection.cursor()
    cursor.execute(sql,request.form['username'])
    cursor.close()
    connection.commit()
    connection.close()

    return redirect(url_for('users_index'))

@app.route('/users/edit/<int:id>', methods=['GET'])
def users_edit(id=0):
    connection = getConnection()
    
    print(id)
    sql = "SELECT * From user WHERE id = %s"
    cursor = connection.cursor()
    user = cursor.execute(sql,id)
    cursor.close()
    connection.close()
    return render_template('users/edit.html', user=user)

@app.route('/users/edit', methods=['POST'])
def users_edit_post():
    # id = request.form['id']
    # user = User.query.get(id)
    # user.username = request.form['username']
    # db.session.commit()

    connection = getConnection()

    sql = "UPDATE user SET username = %s WHERE id = %s"
    cursor = connection.cursor()
    username = request.form['username']
    print(request.form['id'])
    id = cursor.execute("SELECT id from user WHERE username = %s", username)
    print(id,username)
    cursor.execute("UPDATE user SET username = %s WHERE id = %s",(request.form['username'],id))
    print(request.form['username'],request.form['id'])
    cursor.close()
    connection.commit()
    connection.close()
    return redirect(url_for('users_index'))

@app.route('/users/delete', methods=['POST'])
def users_delete_post():
    id = request.form['id']
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('users_index'))

@app.route('/map',methods=['GET'])
def mapview():
    # マップを作成
    mymap = Map(
        identifier="view-side",
        lat=37.4419,
        lng=-122.1419,
        markers=[(37.4419, -122.1419)]
    )
    sndmap = Map(
        identifier="sndmap",
        lat=37.4419,
        lng=-122.1419,
        markers=[
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
             'lat': 37.4419,
             'lng': -122.1419,
             'infobox': "<b>Hello World</b>"
          },
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
             'lat': 37.4300,
             'lng': -122.1400,
             'infobox': "<b>Hello World from other place</b>"
          }
        ]
    )
    return render_template('map.html', mymap=mymap,sndmap=sndmap)

# if __name__ == '__main__':
#     # app.run(host='0.0.0.0', port=80, debug=True)
#     app.run(host='0.0.0.0' , debug=True)
