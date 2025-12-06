# Email Setup for SOS Alerts

## Overview
The SOS button sends email alerts to the emergency contact email when triggered. By default, emails are sent to `dharunikaktm@gmail.com`.

## Configuration

### Option 1: Gmail SMTP (Recommended for Testing)

1. **Enable App Passwords in Gmail:**
   - Go to your Google Account settings
   - Enable 2-Step Verification
   - Generate an App Password for "Mail"
   - Copy the 16-character password

2. **Set Environment Variables:**
   Create a `.env` file in the `backend` directory:
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   SMTP_USE_TLS=True
   FROM_EMAIL=your-email@gmail.com
   EMERGENCY_EMAIL=dharunikaktm@gmail.com
   ```

### Option 2: Other SMTP Providers

For other email providers, update the SMTP settings:
- **Outlook/Hotmail:** `smtp-mail.outlook.com`, port 587
- **Yahoo:** `smtp.mail.yahoo.com`, port 587
- **Custom SMTP:** Use your provider's SMTP settings

### Option 3: Development Mode (No SMTP)

If SMTP is not configured, the system will:
- Log the email content to the console
- Still process the SOS alert
- Return success (for testing purposes)

## Testing

1. Start the backend server
2. Trigger the SOS button from the frontend
3. Check the email inbox at `dharunikaktm@gmail.com`
4. Check backend logs for email sending status

## Email Content

The SOS email includes:
- Subject: "🚨 URGENT: SOS Alert - Help Needed"
- Rider name and ID
- Current location (latitude, longitude)
- Google Maps link to the location
- Timestamp

## Future Enhancements

- SMS notifications via Twilio or similar service
- Phone call alerts
- Multiple emergency contacts
- Customizable email templates

