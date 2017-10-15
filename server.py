from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
import hashlib

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


app = Flask(__name__)
app.secret_key = "GoldenEye007"
mysql = MySQLConnector(app,'the_wall_db')


@app.route('/')
def root():
    print('Going through ROOT')
    print(mysql.query_db("SELECT * FROM users"))

    return render_template('index.html')
@app.route('/wall')
def wall():
    return render_template('wallpage.html')


@app.route('/register', methods=['POST'])
def register():
    validity = True
    session['first_name_input'] = request.form['first_name']
    session['last_name_input'] = request.form['last_name']
    session['email_input'] = request.form['email']
    session['password_input'] = request.form['password']
    hashedPW = hashlib.md5(request.form['password'].encode('utf-8')).hexdigest()

    print(hashedPW)
    session['confirm_password_input'] = request.form['confirm_password']
    print("First name is: ", session['first_name_input'])
    print("Last name is: ", session['last_name_input'])
    print("E-mail is: ", session['email_input'])
    print("Password is: ", session['password_input'])

    query = "SELECT email FROM users WHERE email = :email_from_form"

    data = {
        'email_from_form': session['email_input']
    }
    email_from_db = mysql.query_db(query, data)

    if len(session['first_name_input']) < 2:
        # client didnt put anything in email box
        flash("No less than 2 characters for First Name")
        validity = False
        return redirect('/')
    print('1: ', validity)

    if len(session['last_name_input']) < 2:
        # client didnt put anything in email box
        flash("No less than 2 characters for Last Name")
        validity = False
        return redirect('/')
    print('2: ', validity)

    if email_from_db:
        print('this email already exsists')
        flash('There is already a user with this email.')
        validity = False
        return redirect('/')
    print('3: ', validity)

    if len(session['email_input']) <= 0:
        # client didnt put anything in email box
        flash("Please fill in your E-mail.")
        validity = False
        return redirect('/')
    print('4: ', validity)


    if not EMAIL_REGEX.match(session['email_input']):
        flash('Invalid E-mail Format')
        validity = False
        return redirect('/')
    print('5: ', validity)


    if len(session['password_input']) <= 8:
        print('Password Length needs to be more than 8 characters')
        return redirect('/')
    else:
        print('Password Length meets correct minimum length')
        validity = True
    print('6: ', validity)


    if session['password_input'] != session['confirm_password_input']:
        print('Passwords did not match')
        flash('Passwords did not match!!!')
        validity = False
        return redirect('/')
    else:
        print('Passwords matched')
    print('7: ', validity)

    if validity:
        print('Validation Succeeded')
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, now(), now())"
        data = {
        'last_name': request.form['last_name'],
            'first_name': request.form['first_name'],
            'email': request.form['email'],
            'password': hashedPW
        }
        mysql.query_db(query, data)
        return render_template('WallPage.html')
    else:
        print('Failed validation')
        # failed validation
        return redirect('/')

@app.route('/login', methods=['POST'])
def login_attempt():
    print('Going through /login route')

    session['login_email_input'] = request.form['login_email']
    session['login_password_input'] = request.form['login_password']
    validity = True
    # print(session['login_email_input'])
    #
    password = hashlib.md5(request.form['login_password'].encode('utf-8')).hexdigest()
    email = request.form['login_email']
    user_query = "SELECT * FROM users where users.email = :email AND users.password = :password"
    query_data = { 'email': email, 'password': password}
    user = mysql.query_db(user_query, query_data)
    # # do the necessary logic to login if the user exists, otherwise redirect to login page with error message<br>
    if user:
        return redirect('/wall')
    else:
        flash("Invalid E-mail or password")
        return redirect('/')

app.run(debug=True)
