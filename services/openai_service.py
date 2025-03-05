import logging
import json
import os
import openai
from typing import Dict, Optional, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load OpenAI API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

class OpenAIService:
    def __init__(self):
        self.channel_prompts = {
            'email': "You are Joline, a professional restaurant email assistant from Zevenwacht Restaurant. Respond in a formal, detailed manner suitable for email communication.",
            'whatsapp': "You are Joline, a friendly restaurant WhatsApp assistant from Zevenwacht Restaurant. Keep responses concise and conversational.",
            'sms': "You are Joline, a helpful restaurant SMS assistant from Zevenwacht Restaurant. Keep responses brief and clear due to message length limitations.",
            'voice': "You are Joline, a natural-sounding restaurant voice assistant from Zevenwacht Restaurant. Use conversational language and clear pronunciation.",
            'chat': "You are Joline, an engaging online chat assistant from Zevenwacht Restaurant. Keep responses friendly, helpful, and conversational."
        }
        self.menu_data = self._load_menu_data()

    def _load_menu_data(self) -> Dict:
        """Load menu data from restaurant_data.json"""
        try:
            with open('restaurant_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except Exception as e:
            logger.error(f"Error loading menu data: {str(e)}")
            return {}

    def _get_menu_context(self) -> str:
        """Generate menu context from loaded menu data"""
        if not self.menu_data:
            return ""

        def format_item(item):
            name = item.get('name', '')
            desc = f": {item.get('description')}" if item.get('description') else ""
            price = ""
            if 'price' in item:
                price = f" (R{item['price']})" if item['price'] is not None else " (Market Price)"
            elif 'price_glass' in item and 'price_bottle' in item:
                price = f" (R{item['price_glass']} glass / R{item['price_bottle']} bottle)"
            return f"- {name}{desc}{price}"

        def process_items(items):
            result = ""
            for item in items:
                if 'items' in item:
                    # This is a subsection
                    result += f"\n  {item['name']}:\n"
                    result += "".join(f"  {format_item(subitem)}\n" for subitem in item['items'])
                else:
                    # This is a regular item
                    result += f"{format_item(item)}\n"
            return result

        context = "Available Menu Sections:\n"
        for section in self.menu_data.get('menu_sections', []):
            context += f"\n{section['name']}:\n"
            context += process_items(section['items'])
        return context

    def generate_response(self, message: str, context: str, channel: str = 'chat') -> str:
        """Generate a response using OpenAI's ChatCompletion API with channel-specific adaptations"""
        try:
            # Get channel-specific prompt
            channel_prompt = self.channel_prompts.get(
                channel,
                "You are a helpful restaurant assistant."
            )

            # Add menu context to the enhanced context
            menu_context = self._get_menu_context()
            
            # Create system message with restaurant and menu context
            system_message = f"""{channel_prompt}

You are Joline, a friendly and professional sales agent for Zevenwacht Restaurant. Follow these guidelines EXACTLY:

RESPONSE FORMAT:
You MUST follow these guidelines for structuring your response:

PARAGRAPH 1 (Question Answer):
When the customer asks ANY question (especially about specials, events, or menu items), you MUST answer their question directly and thoroughly here. For example:
- If they ask "Do you have specials next week?", respond with: "Yes, we have several specials next week! Our Tuesday Wine Special offers 50% off all bottles of Zevenwacht Estate wines. On Wednesday, we have our Date Night special with a 3-course meal for two at R595. We also have our Weekend Brunch Special with a complimentary mimosa with any breakfast order on Saturday and Sunday from 8:00-11:00. Our Chef's Weekly Special is grilled kingklip with lemon butter sauce and seasonal vegetables for R195."
- If they ask about hours, menu items, or any other information, provide a complete answer here.

PARAGRAPH 2 (Menu Info - OPTIONAL):
Only include this paragraph if the customer specifically asks about menus OR if you're attaching menus that are relevant to their query:
'I've attached our à la carte menu, wine list, and drinks menu for your reference. Our breakfast and children's menus are available at the restaurant.'

PARAGRAPH 3 (Call to Action):
'Would you like me to help you make a reservation? Please let me know your preferred date and time.'

IMPORTANT NOTES:
- You MUST answer the customer's question in PARAGRAPH 1 before proceeding to other paragraphs.
- ONLY include PARAGRAPH 2 if the customer asks about menus or if menus are directly relevant to their query.
- If the customer doesn't ask a question, you may use PARAGRAPH 1 for a personal connection or skip it entirely.
- NEVER skip answering a direct question from the customer.

CRITICAL RULES:
1. DO NOT add ANY greetings (no 'Dear', 'Hi', 'Hello', etc.)
2. DO NOT add ANY signatures
3. DO NOT add ANY extra spacing
4. DO NOT modify the template text when using PARAGRAPH 2 and 3
5. For PARAGRAPH 1:
   - You MUST answer ANY question the customer asks with specific, detailed information
   - If they ask about specials, ALWAYS include details about our current promotions
   - If they don't ask a question but share personal information, create a personalized response
   - If they do neither, skip PARAGRAPH 1 entirely
6. For PARAGRAPH 2 (Menu Info):
   - ONLY include this if the customer specifically asks about menus
   - ONLY include this if you're attaching menus that are directly relevant to their query
   - SKIP this paragraph entirely if menus are not relevant to the conversation
7. NEVER ignore a customer's question - answering questions is your highest priority
8. ALWAYS include PARAGRAPH 1 if the customer asks ANY question, no matter how simple

The email handler will add the greeting and signature."""
            
            # Add operating hours context
            operating_hours = """
Operating Hours:
- Monday: Closed
- Tuesday to Sunday:
  * Breakfast: 07:30-11:00
  * Main Service: 12:00-22:00
- Kitchen last order: 21:00
"""
            system_message += f"\n\n{operating_hours}"

            # Add menu awareness context
            menu_awareness = """
Available Menus:
- Breakfast Menu (served 07:30-11:00)
- À La Carte Menu (served 12:00-22:00)
- Kiddies Menu (available all day)
- Wine List (featuring our estate wines)
- Drinks Menu (including cocktails, beers, and non-alcoholic beverages)

Current Specials and Promotions:
- Tuesday Wine Special: 50% off all bottles of Zevenwacht Estate wines
- Wednesday Date Night: 3-course meal for two at R595
- Weekend Brunch Special: Complimentary mimosa with any breakfast order (Saturday & Sunday, 8:00-11:00)
- Chef's Weekly Special: Grilled kingklip with lemon butter sauce and seasonal vegetables (R195)

When customers ask about menus or specials, provide relevant information and mention that I can attach the appropriate menu(s) to my response.
"""
            system_message += f"\n\n{menu_awareness}"

            # Check for menu-related and special-related keywords in the message
            message_lower = message.lower()
            menu_keywords = ['menu', 'food', 'drink', 'price', 'burger', 'beer', 'wine', 'dish', 'meal']
            special_keywords = ['special', 'promotion', 'discount', 'offer', 'deal', 'event']
            
            # Include menu context for menu-related queries
            if any(word in message_lower for word in menu_keywords):
                system_message += f"\n\nMenu Information:\n{menu_context}"
                
            # Highlight specials section for special-related queries
            if any(word in message_lower for word in special_keywords):
                system_message += "\n\nThe customer is asking about specials or promotions. Be sure to highlight our current offers in your response."
            
            # Call OpenAI API using ChatCompletion
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # or "gpt-4" if available
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": message}
                ],
                max_tokens=1000,  # Increased from 500 to allow for longer responses
                temperature=0.7,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            # Extract and format the response
            ai_response = response.choices[0].message.content.strip()
            
            # Log successful API call
            logger.info("OpenAI API call successful")
            formatted_response = self._format_response_for_channel(ai_response, channel)
            
            logger.info(f"Generated {channel} response successfully")
            return formatted_response

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble processing your request. Please try again in a moment."

    def _format_response_for_channel(self, response: str, channel: str) -> str:
        """Format the response appropriately for the specific channel"""
        if channel == 'sms':
            return self._truncate_response(response, 160)
        elif channel == 'whatsapp':
            return response
        elif channel == 'email':
            return response
        elif channel == 'voice':
            return response.replace('&', 'and')
        else:
            return response

    def _truncate_response(self, response: str, max_length: int) -> str:
        """Truncate response to specified length while maintaining coherence"""
        if len(response) <= max_length:
            return response
        
        truncated = response[:max_length-3]
        last_period = truncated.rfind('.')
        if last_period > 0:
            return truncated[:last_period + 1]
        return truncated + '...'
        
    def chat_completion(self, system_prompt: str, user_message: str, response_format: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a response using OpenAI's ChatCompletion API with a specific system prompt.
        This is used primarily for the training interface.
        
        Args:
            system_prompt: The system prompt to guide the AI's behavior
            user_message: The user's message
            response_format: Optional format specification for the response (e.g., JSON)
            
        Returns:
            The AI's response as a string
        """
        try:
            # Prepare the API call parameters
            params = {
                "model": "gpt-3.5-turbo",  # or "gpt-4" if available
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 1000,
                "temperature": 0.7,
                "top_p": 1.0,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
            
            # Add response format if specified
            if response_format:
                params["response_format"] = response_format
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(**params)
            
            # Extract and return the response
            ai_response = response.choices[0].message.content.strip()
            logger.info("OpenAI chat completion successful")
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error generating chat completion: {str(e)}")
            return f"Error: {str(e)}"