from services.twilio_service import TwilioService
from services.openai_service import OpenAIService
from services.knowledge_base import KnowledgeBase
from twilio.twiml.voice_response import VoiceResponse

class CallHandler:
    def __init__(self):
        self.twilio_service = TwilioService()
        self.openai_service = OpenAIService()
        self.knowledge_base = KnowledgeBase()

    def handle_incoming_call(self):
        response = VoiceResponse()
        self.twilio_service.handle_incoming_call(response)
        return str(response)

    def handle_recording(self, recording_url):
        # Here we would transcribe the recording and process it
        # For now, we'll use a placeholder response
        context = self.knowledge_base.get_product_context()
        response = self.openai_service.generate_response(
            "Customer asked about our products. Please provide a helpful response.",
            context,
            'voice'
        )
        
        # Create a new response with AI-generated content
        voice_response = VoiceResponse()
        voice_response.say(response)
        voice_response.hangup()
        
        return str(voice_response)