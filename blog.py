from flask import Flask, render_template

# Flask Instance
app = Flask(__name__)

# Router decorator

@app.route('/')

def index():
	return render_template('index.html')

@app.route('/user/<name>/<id>')

def user(name, id):
	num = 35
	return "<h2>Hello {} your id is {}!</h2>".format(name, num)

