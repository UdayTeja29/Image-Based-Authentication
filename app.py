from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')  # Secret key
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///default.db')  # Database URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)

# OTP model
class OTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    expiration_time = db.Column(db.DateTime, nullable=False)

# Create tables in database
with app.app_context():
    db.create_all()

# Utility function to send an email
def send_mail(sender_email, receiver_email, subject, message, smtp_password):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    try:
        server.login(sender_email, smtp_password)
        server.send_message(msg)
        print("Email sent successfully!")
    except smtplib.SMTPAuthenticationError:
        print("SMTP Authentication Error: Check your email or app password.")
    except smtplib.SMTPException as e:
        print(f"SMTP Error: {e}")
    finally:
        server.quit()

# Start page
@app.route('/')
def index():
    return render_template('index.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        selected_images = request.form.getlist('images')

        if not selected_images:
            flash("Please select at least one image.", "error")
            return redirect(url_for('register'))

        # Create a new user and add to the database
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        selected_images = request.form.getlist('images')

        user = User.query.filter_by(email=email, password=password).first()
        if user and selected_images:
            return redirect(url_for('otp', email=email))
        else:
            flash("Invalid credentials or incorrect image selection.", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

# OTP route
@app.route('/otp', methods=['GET', 'POST'])
def otp():
    email = request.args.get('email')

    if not email:
        flash("Email is required to send OTP.", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        otp_input = request.form['otp']
        otp_record = OTP.query.filter_by(email=email, otp_code=otp_input).first()

        # Check if OTP exists and is valid
        if otp_record and otp_record.expiration_time > datetime.now():
            user = User.query.filter_by(email=email).first()
            if user:
                flash(f"Welcome, {user.username}!", "success")
                return render_template("welcome.html", username=user.username)
            else:
                flash("User not found.", "error")
                return redirect(url_for('login'))
        else:
            flash("Invalid or expired OTP", "error")
            return redirect(url_for('otp', email=email))

    # Generate and send OTP
    otp_code = str(random.randint(100000, 999999))  # Generate 6-digit OTP
    expiration_time = datetime.now() + timedelta(minutes=5)

    existing_otp = OTP.query.filter_by(email=email).first()
    if existing_otp:
        existing_otp.otp_code = otp_code
        existing_otp.expiration_time = expiration_time
    else:
        new_otp = OTP(email=email, otp_code=otp_code, expiration_time=expiration_time)
        db.session.add(new_otp)

    db.session.commit()

    # Send the OTP via email
    send_mail(
        os.getenv('SENDER_EMAIL'),
        email,
        "Your OTP Code",
        f"Your OTP code is: {otp_code}",
        os.getenv('SMTP_PASSWORD')
    )

    return render_template('otp.html', email=email)

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
