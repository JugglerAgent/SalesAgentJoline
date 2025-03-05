from services.twilio_service import TwilioService

# Initialize the Twilio service
twilio_service = TwilioService()

# Test message
message = "Hello! This is a test message from your AI Sales Assistant."

# Replace with your phone number (must be verified in trial mode)
to_number = "+27824906997"  # Replace with your actual phone number

# Send the SMS
try:
    response = twilio_service.send_sms(to_number=to_number, message=message)
    print(f"Message sent! SID: {response.sid}")
except Exception as e:
    print(f"Error sending message: {str(e)}")