# Image-Based-Authentication
Image-Based Authentication
A secure image-based authentication system combined with OTP verification. This project allows users to register, log in, and authenticate their identity by selecting images and verifying a One-Time Password (OTP) sent to their email.


Features
User registration with image-based authentication
Secure login requiring both password and image selection
Email-based OTP generation with expiration
PostgreSQL database for secure data storage
Environment-based configuration for sensitive data 


Technologies Used
Backend: Flask (Python) / Node.js (JavaScript)
Database: PostgreSQL
Email Service: Gmail SMTP using Nodemailer (Node.js) or smtplib (Flask)
Frontend: HTML/CSS for user forms
Programming Languages: Python, JavaScript

Set Up the Database
Start your PostgreSQL server and create a database named authentication (or use a different name and update your .env files). Use the following SQL commands to create tables:

sql
-- User table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(120) NOT NULL
);

-- OTP table
CREATE TABLE otps (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    otp VARCHAR(6) NOT NULL,
    expiry TIMESTAMP NOT NULL
);
For image-based authentication, you may need to store user image selections in the database:

sql
Copy code
-- Image selection table
CREATE TABLE user_images (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    image_name VARCHAR(255) NOT NULL
);
