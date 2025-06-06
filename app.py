from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy # sQlite a lightweight, file-based database.
import pdb
import os
from dotenv import load_dotenv
import re
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect

load_dotenv()


# for generating secret random key
# import secrets
# print(secrets.token_hex(16))

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')  # fetch secret key from .env

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME') # email address you want to use to send emails
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD') #not use your normal Gmail password (Google will block it). Use a Gmail App Password instead:
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')


mail = Mail(app) 

s = URLSafeTimedSerializer(app.secret_key) #serializer used to securely generates and verifies the token sent in your reset email.

# Generate absolute path to avoid path issues
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'database', 'users.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
db = SQLAlchemy(app)  #creating a SQLAlchemy object that Links your Flask app to the database.

# Enable CSRF protection
csrf = CSRFProtect(app)

# Define a table (Model)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


# Once run setup_db.py file in console

# Method GET: for viewing page or fetching data
# Method Post: for sending data

def is_strong_password(password):
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return re.match(pattern, password)


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        username = request.form['username']

        password = request.form['password']
        email = request.form['email']

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect('/register')
        
        existing_email = User.query.filter_by(email=email).first()

        if existing_email:
            flash('Email is already registered. Please use a different email.', 'error')
            return redirect('/register')
        

        # Check if password is strong
        if not is_strong_password(password):
            flash('Password must be at least 8 characters long and include an uppercase letter, lowercase letter, number, and special character.', 'error')
            return redirect('/register')

        hashed_password = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed_password)


        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')

        redirect(url_for('register')) 
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        useremail = User.query.filter_by(username=username).first()

        if useremail == None:
            useremail = User.query.filter_by(email=username).first()

        # check_password_hash(user.password, password)
        if useremail and check_password_hash(useremail.password, password):
            session['user_id'] = useremail.id
            session['user_name'] = useremail.username

            flash('Login successful!', 'success')
            return redirect('/dashboard')
        
        else:
            print('invalid')
            flash('Invalid username or password.', 'error')

            return redirect('/login')
        
    return render_template('login.html')


@app.route('/forget', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()

        if user:

            token = s.dumps(email, salt='email-reset')
            link = url_for('reset_password', token=token, _external=True)

            msg = Message('Password Reset Request', sender='rimshayawar2016@gmail.com', recipients=[email])
            msg.body = f'Click the link to reset your password: {link}'
            mail.send(msg)

            flash('Reset link sent to your email.', 'info')

            return redirect('/forget')
        
        else:
            flash('Email not found.', 'error')
            return redirect('/forget')

    return render_template('forget.html')


@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='email-reset', max_age=3600)  # Link valid for 1 hour

    except (SignatureExpired, BadSignature):
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('forgot'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        user = User.query.filter_by(email=email).first() #ORM
        print(user)

        if user:
            user.password = generate_password_hash(new_password)
            db.session.commit()
            flash('Your password has been updated!', 'success')

            return redirect(url_for('login'))
    
    return render_template('reset.html', token=token)


@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return f"Welcome {session['user_name']}!"
    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=False)
