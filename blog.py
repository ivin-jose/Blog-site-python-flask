from flask import Flask, render_template

# Flask Instance
app = Flask(__name__)

# Router decorator

@app.route('/')

def index():
	return render_template('index.html')

@app.route('/user/<name>')

def user(name):
	return render_template('user.html', name = name)

#Custom error pages

#Invalid pages

@app.errorhandler(404)

def page_not_found(e):
	return render_template('errors/404.html')

#Internal server error

@app.errorhandler(500)

def page_not_found(e):
	return render_template('500.html')

