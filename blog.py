from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField
from wtforms.validators import DataRequired
from flask_mysqldb import MySQL
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt


# Flask Instance
app = Flask(__name__)
bcrypt = Bcrypt(app)

# Mysql DataBase 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'somethingfishy1234'
app.config['MYSQL_DB'] = 'blog'

mysql = MySQL(app)

# The Secrete key
app.config['SECRET_KEY'] = "is my secret key"

# class Usersmodel(mysql.Model):
def hashing_password(password):
	@property
	def password(self):
		raise AttributeError('password is not')
	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password, password)		

#ceate a Form Class

class NameForm(FlaskForm):
	name = StringField("Your name", validators = [DataRequired()])
	email = EmailField("Your e-mail", validators = [DataRequired()])
	submit = SubmitField("Submit")

	# Create A String
	def __repr__(self):
		return '<name % r>' % self.name

class UserForm(FlaskForm):
	name = StringField("Your name", validators = [DataRequired()])
	email = EmailField("Your e-mail", validators = [DataRequired()])
	submit = SubmitField("Submit")

	# Create A String
	def __repr__(self):
		return '<name % r>' % self.name

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
	return render_template('errors/505.html')

#Name page router 

@app.route('/name', methods = ['GET', 'POST'])
def name():
	cursor = mysql.connection.cursor()
	cursor.execute("SELECT * FROM users")
	users = cursor.fetchall()
	return render_template('name.html', users = users)

# Adding user 

@app.route('/user/add', methods = ['GET', 'POST'])

def add_user():
	name = None
	email = None
	password = None
	hashpassword = None
	form = UserForm()
	if request.method == 'POST':
		name = request.form['name']
		email = request.form['email']
		password = request.form['password']
		hashpassword = bcrypt.generate_password_hash(password)

		cursor = mysql.connection.cursor()
		add_db = ("INSERT INTO users (name, email, password) VALUES(%s, %s, %s)")
		val = (name, email, hashpassword)
		cursor.execute(add_db, val)
		mysql.connection.commit()
		cursor.close() 

		flash('User added succefullyy')
	return render_template('add_user.html', name=name, form=form, email=email,
	 						password=password,
	 						hashedpass=hashpassword)

@app.route('/update/<int:id>', methods=['GET', 'POST'])

def update_user(id):
	update_name = None
	update_email = None

	cursor = mysql.connection.cursor()
	update_db = ("SELECT * FROM users WHERE id=(%s)")
	values = ([str(id)])
	cursor.execute(update_db, values)
	users = cursor.fetchall()
	cursor.close()

	if request.method == 'POST':
		update_name = request.form.get('updatename')
		update_email = request.form.get('updateemail')
		update_password = request.form.get('updatepassword')

		cursor = mysql.connection.cursor()
		add_db = ("UPDATE users SET name = %s, email = %s, password = %s WHERE id = %s")
		val = (update_name, update_email, update_password, str(id))
		cursor.execute(add_db, val)
		mysql.connection.commit()
		cursor.close()
		flash("User Updated..!!")
		cursor = mysql.connection.cursor()
		cursor.execute("SELECT * FROM users")
		users = cursor.fetchall()
		return render_template('name.html', users = users)
	else:
		return render_template('update_user.html', users = users, id=str(id))

	return render_template('update_user.html', users = users)

# Deleting User 

@app.route('/delete/<int:id>', methods = ['POST', 'GET'])

def delete_user(id):
	delete = ("DELETE FROM users WHERE (id = %s)")
	val = ([str(id)])
	cursor = mysql.connection.cursor()
	cursor.execute(delete, val)
	mysql.connection.commit()
	flash("User Deleted !!!")
	cursor.execute("SELECT * FROM users")
	users = cursor.fetchall()
	cursor.close()
	return render_template('name.html', users = users)	

