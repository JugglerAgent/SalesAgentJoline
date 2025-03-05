import os
import json
import logging
import openai
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIAgent:
    """
    A simple OpenAI-powered agent for restaurant interactions.
    Uses the OpenAI API to generate responses based on restaurant menu data.
    """
    
    def __init__(self):
        """Initialize the OpenAI agent with API key and load restaurant data"""
        # Set API key from environment variable
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            logger.error("OpenAI API key not found in environment variables")
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        
        # Load restaurant data
        self.restaurant_data = self._load_restaurant_data()
        
        # Define channel-specific prompts
        self.channel_prompts = {
            'email': "You are Joline, a professional restaurant email assistant from Zevenwacht Restaurant. Respond in a formal, detailed manner suitable for email communication.",
            'whatsapp': "You are Joline, a friendly restaurant WhatsApp assistant from Zevenwacht Restaurant. Keep responses concise and conversational.",
            'sms': "You are Joline, a helpful restaurant SMS assistant from Zevenwacht Restaurant. Keep responses brief and clear due to message length limitations.",
            'voice': "You are Joline, a natural-sounding restaurant voice assistant from Zevenwacht Restaurant. Use conversational language and clear pronunciation.",
            'chat': "You are Joline, an engaging online chat assistant from Zevenwacht Restaurant. Keep responses friendly, helpful, and conversational."
        }
    
    def _load_restaurant_data(self) -> Dict:
        """Load restaurant data from JSON file"""
        try:
            with open('restaurant_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info("Restaurant data loaded successfully")
                return data
        except Exception as e:
            logger.error(f"Error loading restaurant data: {str(e)}")
            return {}
    
    def _format_menu_context(self) -> str:
        """Format restaurant menu data into a readable context string"""
        if not self.restaurant_data:
            return "Menu information not available."
        
        context = f"Restaurant: {self.restaurant_data.get('name', 'Zevenwacht Restaurant')}\n\n"
        context += "MENU SECTIONS:\n"
        
        for section in self.restaurant_data.get('menu_sections', []):
            section_name = section.get('name', '')
            serving_hours = section.get('serving_hours', '')
            
            context += f"\n{section_name}"
            if serving_hours:
                context += f" ({serving_hours})"
            context += ":\n"
            
            for item in section.get('items', []):
                item_name = item.get('name', '')
                description = item.get('description', '')
                price = item.get('price')
                
                price_str = f"R{price}" if price is not None else "Market Price"
                context += f"- {item_name}: {description} ({price_str})\n"
        
        return context
    
    def generate_response(self, message: str, conversation_history: List[Dict] = None, channel: str = 'chat') -> str:
        """
        Generate a response using OpenAI based on the message, conversation history, and channel
        
        Args:
            message: The user's message
            conversation_history: List of previous messages in the conversation
            channel: The communication channel (email, whatsapp, sms, voice, chat)
            
        Returns:
            A response string
        """
        try:
            # Get channel-specific prompt
            channel_prompt = self.channel_prompts.get(
                channel, 
                "You are Joline, a helpful restaurant assistant from Zevenwacht Restaurant."
            )
            
            # Format conversation history
            history_text = ""
            if conversation_history:
                history_text = "Previous conversation:\n"
                for msg in conversation_history[-5:]:  # Last 5 messages
                    role = msg.get('role', '')
                    content = msg.get('content', '')
                    history_text += f"{role.capitalize()}: {content}\n"
            
            # Check if message is menu-related
            menu_context = ""
            if any(keyword in message.lower() for keyword in 
                  ['menu', 'food', 'eat', 'drink', 'price', 'cost', 'burger', 'beer', 'wine', 'special']):
                menu_context = self._format_menu_context()
            
            # Create prompt for OpenAI
            prompt = f"{channel_prompt}\n\n"
            
            if menu_context:
                prompt += f"MENU INFORMATION:\n{menu_context}\n\n"
            
            if history_text:
                prompt += f"{history_text}\n"
            
            prompt += f"User: {message}\nJoline:"
            
            # Call OpenAI API
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=500,
                temperature=0.7,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                stop=["User:"]
            )
            
            # Extract and format response
            ai_response = response.choices[0].text.strip()
            logger.info("OpenAI response generated successfully")
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {str(e)}")
            return "I apologize, but I'm having trouble processing your request. Please try again in a moment."
    
    def format_response_for_channel(self, response: str, channel: str) -> str:
        """Format the response appropriately for the specific channel"""
        if channel == 'sms':
            # Truncate SMS responses to a reasonable length
            max_length = 160
            if len(response) <= max_length:
                return response
            
            truncated = response[:max_length-3]
            last_period = truncated.rfind('.')
            if last_period > 0:
                return truncated[:last_period + 1]
            return truncated + '...'
            
        elif channel == 'voice':
            # Replace characters that might affect voice synthesis
            return response.replace('&', 'and')
            
        else:
            # No special formatting for other channels
            return response