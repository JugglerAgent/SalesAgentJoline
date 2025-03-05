from twilio.rest import Client
from config.config import Config

class TwilioService:
    def __init__(self):
        self.client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        self.verify_service_sid = Config.TWILIO_VERIFY_SERVICE_SID

    def send_whatsapp(self, to_number, message):
        return self.client.messages.create(
            from_=f'whatsapp:{Config.TWILIO_WHATSAPP_NUMBER}',
            body=message,
            to=f'whatsapp:{to_number}'
        )

    def send_sms(self, to_number, message):
        return self.client.messages.create(
            from_=Config.TWILIO_PHONE_NUMBER,
            body=message,
            to=to_number
        )

    def handle_incoming_call(self, response):
        response.say("Hello! I'm your AI sales assistant. How can I help you today?")
        response.record(maxLength="30")

    def make_outbound_call(self, to_number, message):
        # Structure the TwiML with proper pauses and voice parameters
        twiml = f'''
        <Response>
            <Pause length="2"/>
            <Say voice="alice" language="en-US" rate="0.9">{message}</Say>
            <Pause length="2"/>
            <Say voice="alice" language="en-US" rate="0.9">Thank you for your time. Have a great day!</Say>
        </Response>
        '''
        return self.client.calls.create(
            twiml=twiml,
            to=to_number,
            from_=Config.TWILIO_PHONE_NUMBER
        )

    def send_verification(self, to_number, channel='sms'):
        """Send a verification code to the specified phone number.

        Args:
            to_number (str): The phone number to verify (in E.164 format)
            channel (str): The channel to use for verification ('sms' or 'call')

        Returns:
            The verification instance
        """
        return self.client.verify.v2.services(self.verify_service_sid).verifications.create(
            to=to_number,
            channel=channel
        )

    def check_verification(self, to_number, code):
        """Check a verification code for the specified phone number.

        Args:
            to_number (str): The phone number to verify (in E.164 format)
            code (str): The verification code to check

        Returns:
            The verification check instance
        """
        return self.client.verify.v2.services(self.verify_service_sid).verification_checks.create(
            to=to_number,
            code=code
        )