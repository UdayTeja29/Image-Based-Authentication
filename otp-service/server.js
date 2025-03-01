const express = require('express');
const bodyParser = require('body-parser');
const { generateOTP } = require('./otp'); // Assuming `generateOTP` is a utility function you created
const { Pool } = require('pg');
const nodemailer = require('nodemailer');
require('dotenv').config(); // Load environment variables

// PostgreSQL connection pool using environment variables
const pool = new Pool({
    user: process.env.DB_USER,       // PostgreSQL username
    host: process.env.DB_HOST,       // PostgreSQL host
    database: process.env.DB_NAME,   // PostgreSQL database name
    password: process.env.DB_PASS,   // PostgreSQL password
    port: process.env.DB_PORT,       // PostgreSQL port
});

// Initialize Express app
const app = express();
app.use(bodyParser.json());

// Email configuration using environment variables
const senderEmail = process.env.SENDER_EMAIL;
const smtpPassword = process.env.SMTP_PASSWORD;

// Nodemailer setup
const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: senderEmail,
        pass: smtpPassword,
    },
});

// Function to send email
function sendMail(receiverEmail, subject, message) {
    const mailOptions = {
        from: senderEmail,
        to: receiverEmail,
        subject: subject,
        text: message,
    };

    transporter.sendMail(mailOptions, (error, info) => {
        if (error) {
            console.error('Error sending email:', error);
        } else {
            console.log('Email sent:', info.response);
        }
    });
}

// POST endpoint to send OTP
app.post('/sendOTP', async (req, res) => {
    const userEmail = req.body.email; // Get email from the request
    const otp = generateOTP(); // Generate OTP
    const otpExpiry = new Date(Date.now() + 5 * 60 * 1000); // 5 minutes from now

    try {
        // Insert user into the users table if they don't already exist
        const userResult = await pool.query(
            'INSERT INTO users (email) VALUES ($1) ON CONFLICT (email) DO NOTHING RETURNING id',
            [userEmail]
        );
        const userId = userResult.rows[0]?.id;

        // Insert OTP into the otps table with expiry time
        await pool.query(
            'INSERT INTO otps (user_id, otp, expiry) VALUES ($1, $2, $3)',
            [userId, otp, otpExpiry]
        );

        // Send OTP to the user's email
        const subject = 'Your OTP Code';
        const message = `Your OTP code is ${otp}. It is valid for 5 minutes.`;

        sendMail(userEmail, subject, message);

        // Respond with success
        return res.status(200).send('OTP sent successfully');
    } catch (error) {
        console.error('Error sending OTP:', error);
        return res.status(500).send('Error sending OTP');
    }
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`OTP service is running on http://localhost:${PORT}`);
});
