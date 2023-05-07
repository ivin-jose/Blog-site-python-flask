from flask import Flask, render_template, flash, request, redirect, jsonify, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired
from flask_mysqldb import MySQL
from datetime import datetime, date
from flask_bcrypt import Bcrypt, check_password_hash
from flask_session import Session
from werkzeug.utils import secure_filename
import os
from os.path import realpath, dirname, join
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
# session['userid'] = 123;
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


if __name__ == '__main__':
	app.run()


# Router decorator

@app.route('/')
def index():
    profilepic = None
    rows = []
    userid = session['userid'];
    cursor = mysql.connection.cursor()
    check1 = ("SELECT profilepic FROM users WHERE userid = %s")
    value = [str(userid)]
    cursor.execute(check1, value)
    pic = cursor.fetchall()
        
    for row in pic:
        profilepic = row[0]

    check = ("SELECT blog_content.blog_id, blog_content.userid, blog_content.username, blog_content.heading, blog_content.maincontent, blog_content.date, blog_content.category, users.profilepic  FROM blog_content INNER JOIN users ON blog_content.userid = users.userid LIMIT 12")
    cursor.execute(check)
    rows = cursor.fetchall()
    cursor.close()

    return render_template('index.html', data=rows, profilepic=profilepic)

# @app.route('/')

# def index():
# 	session['userid'] = 123
# 	profilepic = None
# 	cursor = mysql.connection.cursor()
# 	check = ("SELECT blog_content.blog_id, blog_content.userid, blog_content.username, blog_content.heading, blog_content.maincontent, blog_content.date, blog_content.category, users.profilepic  FROM blog_content INNER JOIN users ON blog_content.userid = users.userid LIMIT 12")
# 	cursor.execute(check)
# 	rows = cursor.fetchall()

# 	userid = session['userid'];
# 	check1 = ("SELECT profilepic FROM users WHERE userid = %s")
# 	value = [str(userid)]
# 	cursor.execute(check1, value)
# 	pic = cursor.fetchall()
# 	for row in pic:
# 		profilepic = row[0]

# 	return render_template('index.html', data = rows, profilepic = profilepic)

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
						return redirect("add_profile")
							

	return render_template('signup.html',
	    password = password, 
		username_message = username_message, 
		email_message = email_message)

# Add profile

app.config['UPLOAD_FOLDER'] = 'static/images/profilepics'

@app.route('/add_profile', methods = ['GET', 'POST'])
def add_profile():

	if request.method == 'POST':
		userid = session['userid']
		file = request.files['file']
		path = '../static/images/profilepics/'
		file_path = (path + file.filename)
		data = 'file.read()'
		cursor = mysql.connection.cursor()
		add_db = ("UPDATE users SET profilepic = %s, data = %s WHERE userid = %s")
		val = (file_path, data, str(userid))
		cursor.execute(add_db, val)
		mysql.connection.commit()

		# To move image to folder
		file.save(os.path.join(os.path.abspath(os.path.dirname(realpath(__file__))),app.config['UPLOAD_FOLDER'], file.filename))
		return redirect('profile')

	return render_template('profile_image_uploading.html')	

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
	profilepic = ''

	cursor = mysql.connection.cursor()
	check = ("SELECT blog_content.blog_id, blog_content.userid, blog_content.username, blog_content.heading, blog_content.maincontent, blog_content.date, blog_content.category, users.profilepic  FROM blog_content INNER JOIN users ON blog_content.userid = users.userid WHERE blog_id = %s")
	values = ([str(blog_id)])
	cursor.execute(check, values)
	rows = cursor.fetchall()
	if rows:
		for row in rows:
			uid = row[0]
	else:
		blog_notfound_error = "No Blog Found!"

	check1 = ("SELECT profilepic FROM users WHERE userid = %s")
	value = [str(userid)]
	cursor.execute(check1, value)
	pic = cursor.fetchall()
	for row in pic:
		profilepic = row[0]	

	return render_template('user_blog_full.html', data = rows, username = username, profilepic = profilepic)

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

#  current user profile

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

# @app.route('/edit_profile', methods = ['GET', 'POST'])

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

# edit profile

@app.route('/edit_profile/<int:userid>', methods = ['GET', 'POST'])

def edit_profile(userid):
	blog_notfound_error = None
	cursor = mysql.connection.cursor()
	check = ("SELECT * FROM users WHERE userid = %s")
	values = ([str(userid)])
	cursor.execute(check, values)
	rows = cursor.fetchall()

	if request.method == 'POST':
		name = request.form.get('name')
		username = request.form.get('username')
		email = request.form.get('email')
		about = request.form.get('about')

		cursor = mysql.connection.cursor()
		add_db = ("UPDATE users SET name = %s, username = %s, email = %s, about = %s WHERE userid = %s")
		val = (name, username, email, about, str(userid))
		cursor.execute(add_db, val)
		mysql.connection.commit()
		cursor.close()

		session["username"] = username

		return redirect('/')

	return render_template('edit_profile.html', datas = rows)

# Delete Account

@app.route('/delete_account', methods = ['GET', 'POST'])
def delete_account():
	userid = session['userid']
	if request.method == 'POST':
		cursor = mysql.connection.cursor()
		check = ("DELETE FROM users WHERE userid = %s")
		values = ([str(userid)])
		cursor.execute(check, values)
		mysql.connection.commit()

		session["username"] = None
		session["password"] = None
		session["userid"] = None

		cursor = mysql.connection.cursor()
		check = ("SELECT * FROM blog_content")
		cursor.execute(check)
		rows = cursor.fetchall()

	return render_template('index.html', data = rows)	

#search blog

@app.route('/search_blog', methods = ['GET', 'POST'])
def search_blog():
	search_element = ''
	blog_notfound_error = ''
	blogs = ''
	if request.method == 'POST':
		search_element = request.form.get('search')
		search = ('%' + search_element + '%');
		cursor = mysql.connection.cursor()
		check = ("SELECT blog_content.blog_id, blog_content.userid, blog_content.username, blog_content.heading, blog_content.maincontent, blog_content.date, blog_content.category, users.profilepic FROM blog_content INNER JOIN users ON (blog_content.userid = users.userid) WHERE maincontent LIKE %s OR heading LIKE %s OR category LIKE %s OR blog_content.username LIKE %s")
		values = ([str(search)], [str(search)], [str(search)], [str(search)])
		cursor.execute(check, values)
		blogs = cursor.fetchall()
		if blogs:
			blog_notfound_error = ""
			for row in blogs:
				uid = row[0]
		else:
			blog_notfound_error = "No Blog Found!"


	return render_template('search_display.html', data = blogs, blog_notfound_error = blog_notfound_error)	

# Ask questions category

@app.route('/ask_questions_category', methods = ['GET', 'POST'])
def ask_questions_category():
	cursor = mysql.connection.cursor()
	check = ("SELECT * FROM questioncategoris")
	cursor.execute(check)
	rows = cursor.fetchall()
	return render_template('ask_question_category.html', qcategory = rows)

# Ask questions subcategory

@app.route('/ask_questions_subcategory/<category>', methods = ['GET', 'POST'])
def ask_questions_subcategory(category):
	cursor = mysql.connection.cursor()
	check = ("SELECT subcategory, category FROM subcategories WHERE category = %s")
	values = ([str(category)])
	cursor.execute(check, values)
	rows = cursor.fetchall()

	return render_template('ask_questions_subcategory.html', qsubcategory = rows)	

# Ask questions form

@app.route('/ask_question_form/<category>/<subcategory>', methods = ['GET', 'POST'])
def ask_question_form(category, subcategory):
	flag = True
	if request.method == 'POST':
		userid = session['userid']
		question = request.form.get('question')
		answer = 'No Answers Yet'
		answereduserid = 'none'

		cursor = mysql.connection.cursor()
		add_db = ("INSERT INTO questions (userid, question, answer, answereduserid, category, subcategory) VALUES (%s, %s, %s, %s, %s, %s)")
		val = (userid, question, answer, answereduserid, category, subcategory)
		cursor.execute(add_db, val)
		mysql.connection.commit()
		flag = False

	return render_template('ask_question_form.html', subcategory = subcategory, flag = flag)

# Answer questions category

@app.route('/answer_questions_category', methods = ['GET', 'POST'])
def answer_questions_category():
	cursor = mysql.connection.cursor()
	check = ("SELECT * FROM questioncategoris")
	cursor.execute(check)
	rows = cursor.fetchall()
	return render_template('answer_question_category.html', qcategory = rows)

# Ask questions subcategory

@app.route('/answer_questions_subcategory/<category>', methods = ['GET', 'POST'])
def answer_questions_subcategory(category):
	cursor = mysql.connection.cursor()
	check = ("SELECT subcategory, category FROM subcategories WHERE category = %s")
	values = ([str(category)])
	cursor.execute(check, values)
	rows = cursor.fetchall()

	return render_template('answer_questions_subcategory.html', qsubcategory = rows)

# displaying questions

@app.route('/answerquestions/<category>/<subcategory>', methods = ['GET', 'POST'])
def answerquestions(category, subcategory):
	answer = 'No Answers Yet'
	cursor = mysql.connection.cursor()
	check = ("SELECT questionid, question FROM questions WHERE category = %s AND subcategory = %s AND answer = %s")
	values = ([str(category)], [str(subcategory)], answer)
	cursor.execute(check, values)
	rows = cursor.fetchall()
	if rows:
		qnotfound = ""
	else:
	 	qnotfound = "Not Found any questions.!"	

	return render_template('answer_the_questions.html', datas = rows, qnotfound = qnotfound)	

# Answering section of single questions

@app.route('/answering/<int:qid>', methods = ['GET', 'POST'])
def answering(qid):
	cursor = mysql.connection.cursor()
	check = ("SELECT questions.questionid, questions.userid, questions.question, users.username FROM users INNER JOIN questions ON users.userid = questions.userid WHERE questions.questionid = %s")
	values = ([str(qid)])
	cursor.execute(check, values)
	rows = cursor.fetchall()

	check1 = ("SELECT answers.answerid, answers.userid, answers.answer, users.username FROM users INNER JOIN answers ON users.userid = answers.userid WHERE answers.questionid = %s")
	value1 = ([str(qid)])
	cursor.execute(check1, value1)
	answers = cursor.fetchall()

	if request.method == 'POST':
		userid = session['userid']
		answer = request.form.get('answer')
		questionid = request.form.get('questionid')
		questionuserid = request.form.get('questionuserid')

		cursor = mysql.connection.cursor()
		add_db = ("INSERT INTO answers (userid, answer, questionid, questionuserid) VALUES (%s, %s, %s, %s)")
		val = (userid, answer, questionid, questionuserid)
		cursor.execute(add_db, val)
		mysql.connection.commit()

	return render_template('answering.html', data = rows, answers = answers)	


@app.route('/uploadanswer', methods = ['GET', 'POST'])
def uploadanswer():
	answer = 'Y'
	message = "Answer submitted succefuly"
	if request.method == 'POST':
		userid = session['userid']
		answer = request.form.get('answer')
		questionid = request.form.get('questionid')
		questionuserid = request.form.get('questionuserid')

		cursor = mysql.connection.cursor()
		add_db = ("INSERT INTO answers (userid, answer, questionid, questionuserid) VALUES (%s, %s, %s, %s)")
		val = (userid, answer, questionid, questionuserid)
		cursor.execute(add_db, val)
		mysql.connection.commit()

		cursor = mysql.connection.cursor()
		update = ("UPDATE questions SET answer = %s, answereduserid = %s WHERE questionid = %s")
		vale = (answer, [str(userid)], [str(questionid)])
		cursor.execute(update, vale)
		mysql.connection.commit()
		cursor.close()

	return redirect('/')

# search questions

@app.route('/search_question', methods = ['GET', 'POST'])
def search_question():
	blogs = ''
	qnot_found =''
	if request.method == 'POST':
		search_element = request.form.get('qsearch')
		search = ('%' + search_element + '%');
		cursor = mysql.connection.cursor()
		check = ("SELECT users.username, questions.questionid, questions.userid, questions.question, answers.userid, answers.answerid, answers.answer, answers.questionid, questions.subcategory FROM answers INNER JOIN questions ON (answers.questionid = questions.questionid) INNER JOIN users ON (users.userid = questions.userid) WHERE subcategory LIKE %s OR category LIKE %s OR questions.question LIKE %s OR answers.answer LIKE %s")
		values = ([str(search)], [str(search)], [str(search)], [str(search)])
		cursor.execute(check, values)
		blogs = cursor.fetchall()
		if blogs:
			qnot_found = ""
			for row in blogs:
				uid = row[0]
		else:
			qnot_found = "No Blog Found!"

	return render_template('search_question.html',  data = blogs, qnot_found = qnot_found)

# view user answer

@app.route('/view_user_answer', methods = ['GET', 'POST'])
def view_user_answer():
	blogs = ''
	qnot_found ='Answered by : You'
	userid = session['userid']
	flag = True

	cursor = mysql.connection.cursor()
	check = ("SELECT users.username, questions.questionid, questions.userid, questions.question, answers.userid, answers.answerid, answers.answer, answers.questionid, questions.subcategory FROM questions INNER JOIN answers ON (questions.questionid = answers.questionid) INNER JOIN users ON (users.userid = questions.userid) WHERE answers.userid = %s")
	values = ([str(userid)])
	cursor.execute(check, values)
	blogs = cursor.fetchall()

	if blogs:
		qnot_found = "Answered by : You"
		for row in blogs:
			uid = row[0]
	else:
		qnot_found = ""

	return render_template('search_question.html',  data = blogs, qnot_found = qnot_found, flag = flag)

# view user questions

@app.route('/view_user_question', methods = ['GET', 'POST'])
def view_user_question():
	blogs = ''
	qnot_found ='Questioned by : You'
	userid = session['userid']

	cursor = mysql.connection.cursor()
	check = ("SELECT questions.questionid, questions.userid, questions.question, questions.subcategory, questions.answer, users.username FROM questions LEFT JOIN users ON(users.userid = questions.answereduserid) WHERE questions.userid = %s")
	values = ([str(userid)])
	cursor.execute(check, values)
	blogs = cursor.fetchall()

	if blogs:
		qnot_found = "Questioned by : You"
		for row in blogs:
			uid = row[0]
	else:
		qnot_found = ""

	return render_template('view_questions.html',  data = blogs, qnot_found = qnot_found)

# deleting question

@app.route('/delete_user_q/<int:id>', methods = ['GET', 'POST'])
def delete_user_q(id):
	blogs = ''
	qnot_found ='Questioned by : You'
	userid = session['userid']

	cursor = mysql.connection.cursor()
	check = ("DELETE FROM questions WHERE questionid = %s")
	values = ([str(id)])
	cursor.execute(check, values)
	mysql.connection.commit()

	cursor = mysql.connection.cursor()
	check = ("SELECT users.username, questions.questionid, questions.userid, questions.question, questions.subcategory, questions.question FROM questions INNER JOIN users ON (users.userid = questions.answereduserid) WHERE questions.userid = %s")
	values = ([str(userid)])
	cursor.execute(check, values)
	blogs = cursor.fetchall()
	return render_template('view_questions.html',  data = blogs, qnot_found = qnot_found)

# deleting question

@app.route('/delete_user_a/<int:aid>/<int:qid>', methods = ['GET', 'POST'])
def delete_user_a(aid, qid):
	blogs = ''
	qnot_found ='Questioned by : You'
	userid = session['userid']
	flag = True
	answer = 'No Answers Yet'
	answereduserid = 'none'

# need to delete a column from questions and answers 
	cursor = mysql.connection.cursor()
	check = ("DELETE FROM answers WHERE answerid = %s")
	values = ([str(aid)])
	cursor.execute(check, values)
	mysql.connection.commit()

	cursor = mysql.connection.cursor()
	update = ("UPDATE questions SET answer = %s, answereduserid = %s WHERE questionid = %s")
	vale = (answer, [str(answereduserid)], [str(qid)])
	cursor.execute(update, vale)
	mysql.connection.commit()
	cursor.close()

	cursor = mysql.connection.cursor()
	check = ("SELECT users.username, questions.questionid, questions.userid, questions.question, answers.userid, answers.answerid, answers.answer, answers.questionid, questions.subcategory FROM questions INNER JOIN answers ON (questions.questionid = answers.questionid) INNER JOIN users ON (users.userid = questions.userid) WHERE answers.userid = %s")
	values = ([str(userid)])
	cursor.execute(check, values)
	blogs = cursor.fetchall()

	return render_template('search_question.html',  data = blogs, qnot_found = qnot_found, flag = flag)

	