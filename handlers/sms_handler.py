from services.twilio_service import TwilioService
from services.openai_service import OpenAIService
from services.knowledge_base import KnowledgeBase

class SMSHandler:
    def __init__(self):
        self.twilio_service = TwilioService()
        self.openai_service = OpenAIService()
        self.knowledge_base = KnowledgeBase()

    def handle_incoming_message(self, message_body, from_number):
        # Get product context and generate AI response
        context = self.knowledge_base.get_product_context()
        response = self.openai_service.generate_response(
            message_body,
            context,
            'sms'
        )

        # Send the response back via SMS
        return self.twilio_service.send_sms(
            to_number=from_number,
            message=response
        )

    def send_message(self, to_number, message):
        return self.twilio_service.send_sms(
            to_number=to_number,
            message=message
        )