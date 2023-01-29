from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


# Flask Instance
app = Flask(__name__)
app.config['SECRET_KEY'] = "is my secret key"


#ceate a Form Class

class NameForm(FlaskForm):
	name = StringField("Your name", validators = [DataRequired()])
	submit = SubmitField("Submit")


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

#Name page router 

@app.route('/name', methods = ['GET', 'POST'])
def name():
	name = None
	form = NameForm()
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''
		flash(" Succefully Added!")
	return render_template('name.html', name = name, form = form)

