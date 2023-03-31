from flask import Flask, render_template, flash, request, redirect, jsonify, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired
from flask_mysqldb import MySQL
from datetime import datetime, date
from flask_bcrypt import Bcrypt, check_password_hash
from flask_session import Session


# Flask Instance
app = Flask(__name__)
bcrypt = Bcrypt(app)

# Mysql DataBase 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'somethingfishy1234'
app.config['MYSQL_DB'] = 'blog'

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
mysql = MySQL(app)

# The Secrete key
app.config['SECRET_KEY'] = "is my secret key"

# sessiom variables

# session["username"] = None
# session["password"] = None
# session["userid"] = None

# class Usersmodel(mysql.Model):
def hash_password(password):
	hashpassword = bcrypt.generate_password_hash(password)
	return hashpassword

#checking hashed password with plain text

def check_hash_password(hashed, password):
	checked_pw = check_password_hash(hashed, password)
	return checked_pw	

#ceate a Form Class

class PasswordForm(FlaskForm):
	email = StringField("Your e-mail", validators = [DataRequired()])
	password = PasswordField("Your password", validators = [DataRequired()])
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
	cursor = mysql.connection.cursor()
	check = ("SELECT * FROM blog_content")
	cursor.execute(check)
	rows = cursor.fetchall()
	return render_template('index.html', data = rows)

#Custom error pages

#Invalid pages

@app.errorhandler(404)

def page_not_found(e):
	return render_template('errors/404.html')

#Internal server error

@app.errorhandler(500)

def page_not_found(e):
	return render_template('errors/505.html')

# login

@app.route('/signup', methods = ['GET', 'POST'])

def signup():
	name = None
	username = None
	email = None
	password = None
	about = None
	username_message = ''
	email_message = ''
	uid = None
	today_date = date.today()

	if request.method == 'POST':
		name = request.form.get('name')
		username = request.form.get('username')
		email = request.form.get('email')
		password = request.form.get('password')
		about = request.form.get('about')

		if username and request.method == 'POST':		
			cursor = mysql.connection.cursor()
			check = ("SELECT * FROM users WHERE username=%s")
			values = ([str(username)])
			cursor.execute(check, values)
			rows = cursor.fetchone()
			if rows:
				return jsonify("username exist")
			else:
				if email and request.method == 'POST':		
					cursor = mysql.connection.cursor()
					check = ("SELECT * FROM users WHERE email=%s")
					values = ([str(email)])
					cursor.execute(check, values)
					rows = cursor.fetchone()
					if rows:
						return jsonify("already registered")
					else:
						cursor = mysql.connection.cursor()
						add_db = ("INSERT INTO users (name, username, email, password, date, about) VALUES(%s, %s, %s, %s, %s, %s)")
						val = (name, username, email, password, today_date, about)
						cursor.execute(add_db, val)
						mysql.connection.commit()
						
						cursor.execute("SELECT userid FROM users WHERE username = username AND password = password")
						users = cursor.fetchall()
						for row in users:
							uid = row[0];

						session["username"] = username
						session["password"] = password
						session["userid"] = uid
							
						cursor.close()
						return redirect("/")
							

	return render_template('signup.html',
	    password = password, 
		username_message = username_message, 
		email_message = email_message)

# Logout session

@app.route('/logout')

def logout():
	session["username"] = None
	session["password"] = None
	session["userid"] = None
	return redirect('/')

# signin / login

@app.route('/login', methods = ['GET', 'POST'])

def login():
	login_error_msg = ''
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		cursor = mysql.connection.cursor()
		check = ("SELECT * FROM users WHERE username = %s AND password = %s")
		values = (username, password)
		cursor.execute(check, values)
		rows = cursor.fetchall()
		if rows:
			for row in rows:
				uid = row[0]
			session["username"] = username
			session["password"] = password
			session["userid"] = uid
			return redirect('/')
		else:
			login_error_msg = "Something wrong"	

	return render_template('login.html', login_error_msg = login_error_msg)

# user blog 

@app.route('/userblog', methods = ['GET', 'POST'])
def userblog():
	userid = session['userid']
	blog_notfound_error = ''
	x_date = datetime.now()
	today_date = (x_date.strftime("%d-%B-%Y"))

	cursor = mysql.connection.cursor()
	check = ("SELECT * FROM blog_content WHERE userid = %s")
	values = ([str(userid)])
	cursor.execute(check, values)
	blogs = cursor.fetchall()
	if blogs:
		for row in blogs:
			uid = row[0]
	else:
		blog_notfound_error = "No Blog Found!"

	if request.method == 'POST':
		heading = request.form.get('blog_heading')
		blog_content = request.form.get('blog_content')
		blog_category = request.form.get('blog_category')
		username = session['username']
		user_id = ([str(userid)])

		cursor = mysql.connection.cursor()
		add_blog = ("INSERT INTO blog_content (userid, username, heading, maincontent, date, category) VALUES(%s, %s, %s, %s, %s, %s)")
		blog_val = (userid, username, heading, blog_content, today_date, blog_category)
		cursor.execute(add_blog, blog_val)
		mysql.connection.commit()
		cursor.close()

	return render_template('/user_blog.html', blog_notfound_error = blog_notfound_error, data = blogs)

# blog complete page 

@app.route('/user_blog_full/<int:blog_id>', methods = ['GET', 'POST'])

def user_blog_full(blog_id):
	userid = session['userid']
	username = session['username']
	blog_notfound_error = ''

	cursor = mysql.connection.cursor()
	check = ("SELECT * FROM blog_content WHERE blog_id = %s")
	values = ([str(blog_id)])
	cursor.execute(check, values)
	rows = cursor.fetchall()
	if rows:
		for row in rows:
			uid = row[0]
	else:
		blog_notfound_error = "No Blog Found!"

	return render_template('user_blog_full.html', data = rows, username = username)

# blog update

@app.route('/update_blog/<int:blogid>', methods = ['GET', 'POST'])

def update_blog(blogid):
	x_date = datetime.now()
	today_date = (x_date.strftime("%d-%B-%Y"))

	cursor = mysql.connection.cursor()
	check = ("SELECT * FROM blog_content WHERE blog_id = %s")
	values = ([str(blogid)])
	cursor.execute(check, values)
	blogs = cursor.fetchall()
	cursor.close()

	if request.method == 'POST':
		blog_id = request.form.get('blog_id')
		userid = request.form.get('userid')
		username = request.form.get('username')

		headings = request.form.get('heading')
		category = request.form.get('category')
		maincontent = request.form.get('maincontent')

		cursor = mysql.connection.cursor()
		add_db = ("UPDATE blog_content SET heading = %s, maincontent = %s, date = %s, category = %s WHERE blog_id = %s")
		val = (headings, maincontent, today_date, category, str(blog_id))
		cursor.execute(add_db, val)
		mysql.connection.commit()
		cursor.close()

		return redirect('/')

	return render_template('update_blog.html', data = blogs)

#delete blog

@app.route('/delete_blog/<int:blogid>')

def delete_blog(blogid):
	cursor = mysql.connection.cursor()
	dlt_blog = ("DELETE FROM blog_content WHERE blog_id = %s")
	value = ([str(blogid)])
	cursor.execute(dlt_blog, value)
	mysql.connection.commit()
	cursor.close()
	return redirect('/')	

# user profile

@app.route('/profile', methods = ['GET', 'POST'])

def profile():
	blog_notfound_error = None
	userid = session['userid']
	cursor = mysql.connection.cursor()
	check = ("SELECT * FROM users WHERE userid = %s")
	values = ([str(userid)])
	cursor.execute(check, values)
	rows = cursor.fetchall()

	cursor = mysql.connection.cursor()
	check = ("SELECT * FROM blog_content WHERE userid = %s")
	values = ([str(userid)])
	cursor.execute(check, values)
	blogs = cursor.fetchall()
	if blogs:
		blog_notfound_error = ""
		for row in blogs:
			uid = row[0]
	else:
		blog_notfound_error = "No Blog Found!"

	return render_template('profile.html', datas = rows, blogs = blogs, blog_notfound_error = blog_notfound_error)

@app.route('/edit_profile', methods = ['GET', 'POST'])

#edit user profile

def edit_profile():
	userid = session['userid']

	if request.method == 'POST':
		uname = request.form.get('name')
		username = request.form.get('username')
		email = request.form.get('email')
		cursor = mysql.connection.cursor()
		add_db = ("UPDATE users SET name = %s, username = %s, email = %s WHERE userid = %s")
		val = (uname, username, email, str(userid))
		cursor.execute(add_db, val)
		mysql.connection.commit()
		cursor.close()
		session["username"] = username
	return redirect('/profile')	

# Displaying author page when blog link clicked

@app.route('/user_profile/<int:userid>', methods = ['GET', 'POST'])

def user_profile(userid):
	blog_notfound_error = None
	cursor = mysql.connection.cursor()
	check = ("SELECT * FROM users WHERE userid = %s")
	values = ([str(userid)])
	cursor.execute(check, values)
	rows = cursor.fetchall()

	cursor = mysql.connection.cursor()
	check = ("SELECT * FROM blog_content WHERE userid = %s")
	values = ([str(userid)])
	cursor.execute(check, values)
	blogs = cursor.fetchall()
	if blogs:
		blog_notfound_error = ""
		for row in blogs:
			uid = row[0]
	else:
		blog_notfound_error = "No Blog Found!"

	return render_template('profile.html', datas = rows, blogs = blogs,
	 blog_notfound_error = blog_notfound_error)


# #Name page router 

# @app.route('/name', methods = ['GET', 'POST'])
# def name():
# 	cursor = mysql.connection.cursor()
# 	cursor.execute("SELECT * FROM users")
# 	users = cursor.fetchall()
# 	return render_template('name.html', users = users)

# # Adding user 

# @app.route('/user/add', methods = ['GET', 'POST'])

# def add_user():
# 	name = None
# 	email = None
# 	password = None
# 	hashpassword = None
# 	form = UserForm()
# 	if request.method == 'POST':
# 		name = request.form['name']
# 		email = request.form['email']
# 		password = request.form['password']
# 		hashpassword = hash_password(password)
# 		today_date = date.today()

# 		cursor = mysql.connection.cursor()
# 		add_db = ("INSERT INTO users (name, email, date, password) VALUES(%s, %s, %s, %s)")
# 		val = (name, email, today_date, hashpassword)
# 		cursor.execute(add_db, val)
# 		mysql.connection.commit()
# 		cursor.close() 

# 		flash('User added succefullyy')
# 	return render_template('add_user.html', name=name, form=form, email=email,
# 	 						password=password,
# 	 						hashedpass=hashpassword)

# @app.route('/update/<int:id>', methods=['GET', 'POST'])

# def update_user(id):
# 	update_name = None
# 	update_email = None

# 	cursor = mysql.connection.cursor()
# 	update_db = ("SELECT * FROM users WHERE id=(%s)")
# 	values = ([str(id)])
# 	cursor.execute(update_db, values)
# 	users = cursor.fetchall()
# 	cursor.close()

# 	if request.method == 'POST':
# 		update_name = request.form.get('updatename')
# 		update_email = request.form.get('updateemail')
# 		update_password = request.form.get('updatepassword')
# 		today_date = date.today()

# 		cursor = mysql.connection.cursor()
# 		add_db = ("UPDATE users SET name = %s, email = %s, date = %s, password = %s WHERE id = %s")
# 		val = (update_name, update_email, today_date, update_password, str(id))
# 		cursor.execute(add_db, val)
# 		mysql.connection.commit()
# 		cursor.close()
# 		flash("User Updated..!!")
# 		cursor = mysql.connection.cursor()
# 		cursor.execute("SELECT * FROM users")
# 		users = cursor.fetchall()
# 		return render_template('name.html', users = users)
# 	else:
# 		return render_template('update_user.html', users = users, id=str(id))

# 	return render_template('update_user.html', users = users)

# # Deleting User 

# @app.route('/delete/<int:id>', methods = ['POST', 'GET'])

# def delete_user(id):
# 	delete = ("DELETE FROM users WHERE (id = %s)")
# 	val = ([str(id)])
# 	cursor = mysql.connection.cursor()
# 	cursor.execute(delete, val)
# 	mysql.connection.commit()
# 	flash("User Deleted !!!")
# 	cursor.execute("SELECT * FROM users")
# 	users = cursor.fetchall()
# 	cursor.close()
# 	return render_template('name.html', users = users)

# # checking email and passwords

# @app.route('/user', methods = ['POST', 'GET'])

# def user():
# 	name = None
# 	email = None
# 	password = None
# 	hashpassword = None
# 	users = None
# 	val = False
# 	form = PasswordForm()
# 	if form.validate_on_submit():
# 		email = form.email.data
# 		password = form.password.data

# 		cursor = mysql.connection.cursor()
# 		user_info = ("SELECT * FROM users WHERE email=(%s)")
# 		values = ([email])
# 		cursor.execute(user_info, values)
# 		users = cursor.fetchall()
# 		for user in users:
# 			if check_hash_password(user[4], password) == True:
# 				val = True
# 				name = user[1]
# 			else:
# 				val = False	
# 		cursor.close() 

# 		form.email.data = ''
# 		form.password.data = ''

# 	return render_template('user.html', name = name, email = email,
# 			password = password, user = users, val = val,
# 			form = form)


