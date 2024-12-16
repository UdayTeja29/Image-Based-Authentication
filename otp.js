const crypto = require('crypto');
require('dotenv').config(); // Load environment variables from a `.env` file

function generateOTP() {
    const secret = process.env.OTP_SECRET || 'defaultsecretkey'; // Use environment variable or a default key for development
    const time = Math.floor(Date.now() / 1000); // Current time in seconds
    const hmac = crypto.createHmac('sha1', secret); // Create HMAC using SHA1 and the secret key
    hmac.update(String(time)); // Update HMAC with the current time
    const otp = hmac.digest('hex').slice(0, 6); // Generate a 6-character OTP (hex slice)
    return otp;
}

module.exports = { generateOTP };
