from .openai_service import OpenAIService
from .knowledge_base import KnowledgeBase
from .menu_validator import MenuValidator
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatAgent:
    def __init__(self):
        self.openai_service = OpenAIService()
        self.knowledge_base = KnowledgeBase()
        self.menu_validator = MenuValidator()
        self.conversation_history = {}
        self.greeting_message = "Good day, I'm Joline from Zevenwacht Restaurant. How may I assist you today?"

    def _get_conversation_key(self, channel, user_id):
        return f"{channel}:{user_id}"

    def _get_conversation_context(self, conversation_key, channel):
        if conversation_key not in self.conversation_history:
            self.conversation_history[conversation_key] = [{
                'role': 'assistant',
                'content': self.greeting_message,
                'timestamp': datetime.now().isoformat(),
                'channel': channel
            }]
        
        # Get menu and product context
        context = self.knowledge_base.get_product_context()
        menu_context = self.menu_validator.get_current_menu()
        context = f"{context}\n\nCurrent Menu:\n{menu_context}"
        
        # Add conversation history context with channel awareness
        history = self.conversation_history[conversation_key]
        if history:
            context += "\n\nRecent conversation history:\n"
            for msg in history[-5:]:
                context += f"[{msg.get('channel', 'unknown')}] {msg['role']}: {msg['content']}\n"
        
        return context

    def handle_message(self, message, channel, user_id):
        """Handle incoming messages from any channel (SMS, WhatsApp, Voice, Email)"""
        try:
            conversation_key = self._get_conversation_key(channel, user_id)
            logger.info(f"Handling {channel} message from {user_id}")
            
            # Add user message to history with channel info
            self.conversation_history.setdefault(conversation_key, [{
                'role': 'assistant',
                'content': self.greeting_message,
                'timestamp': datetime.now().isoformat(),
                'channel': channel
            }]).append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().isoformat(),
                'channel': channel
            })
            
            # Get context and generate response with OpenAI
            context = self._get_conversation_context(conversation_key, channel)
            response = self.openai_service.generate_response(message, context, channel)
            
            # Validate response against menu items
            validated_response = self.menu_validator.validate_and_correct_response(response)
            
            # Add agent response to history
            self.conversation_history[conversation_key].append({
                'role': 'assistant',
                'content': validated_response,
                'timestamp': datetime.now().isoformat(),
                'channel': channel
            })
            
            logger.info(f"Successfully processed {channel} message from {user_id}")
            return validated_response
            
        except Exception as e:
            logger.error(f"Error handling {channel} message: {str(e)}")
            return "I apologize, but I'm having trouble processing your request. Please try again in a moment."

    def get_conversation_history(self, channel, user_id):
        """Retrieve the conversation history for a specific channel and user"""
        conversation_key = self._get_conversation_key(channel, user_id)
        return self.conversation_history.get(conversation_key, [])

    def clear_conversation_history(self, channel, user_id):
        """Clear the conversation history for a specific channel and user"""
        conversation_key = self._get_conversation_key(channel, user_id)
        if conversation_key in self.conversation_history:
            del self.conversation_history[conversation_key]