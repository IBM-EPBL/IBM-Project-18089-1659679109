from flask import Flask, render_template, request, redirect, url_for, session,Response
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import cv2
from keras.models import load_model
import numpy as np
from gtts import gTTS
import os
from keras.preprocessing import image
from skimage.transform import resize
from playsound import playsound
import pyttsx3
import speech_recognition as sr
from PIL import Image
import matplotlib.pyplot as plt


app = Flask(__name__)

index = ['A','B','C','D','E','F','G','H','I']
model=load_model('model.h5')
video = cv2.VideoCapture(0) 
r = sr.Recognizer()
app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Prathidp28#'
app.config['MYSQL_DB'] = 'applogin'

mysql = MySQL(app)


def SpeakText(command):
	engine = pyttsx3.init()
	engine.say(command)
	engine.runAndWait()

def generate_frames():
	while (video.isOpened()): 
		success, frame = video.read() 
		cv2.imwrite('frame.jpg', frame) 
		img=resize(frame,(64,64,1))
		img=np.expand_dims(img,axis=0)
		if(np.max(img)>1):
			img = img/255.0

		predict_x=model.predict(img)
		print(predict_x)
		predict=np.argmax(predict_x,axis=1)
		y=predict[0]
		SpeakText(index[y])
		copy = frame.copy() 
		cv2.rectangle(copy, (320, 100), (620, 400), (255, 0, 0), 5) 
		cv2.putText(frame, "The Predicted Alphabet : " + str(index[y]), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4) 
		cv2.imshow('frame', frame) 
		if cv2.waitKey(1) & 0xFF == ord('q'): 
			break 
		ret, buffer = cv2.imencode('.jpg', frame)
		frame = buffer.tobytes()
		yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
@app.route('/homepage', methods =['GET', 'POST'])
def homepage():
	return render_template('homepage.html')


@app.route('/services', methods =['GET', 'POST'])
def services():
	return render_template('services.html')

@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
		account = cursor.fetchone()
		if account:
			session['loggedin'] = True
			session['id'] = account['id']
			session['username'] = account['username']
			msg = 'Logged in successfully !'
			return render_template('services.html', msg = msg)
		else:
			msg = 'Incorrect username / password !'
	return render_template('login.html', msg = msg)

@app.route('/signtospeech', methods =['GET', 'POST'])
def signtospeech():
    return render_template('signtospeech.html')

@app.route('/speechtosign', methods =['GET', 'POST'])
def speechtosign():
    return render_template('speechtosign.html')


@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email:
			msg = 'Please fill out the form !'
		else:
			cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
			mysql.connection.commit()
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
	return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

