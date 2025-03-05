from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MenuValidator:
    def __init__(self):
        self.menu_cache = {}
        self.menu_cache_timestamp = None
        self.cache_duration = 3600  # Cache menu for 1 hour

    def get_current_menu(self):
        """Retrieve the current menu based on time of day and day of week"""
        try:
            current_time = datetime.now()
            
            # Check if we have a valid cached menu
            if (self.menu_cache_timestamp and 
                (current_time - self.menu_cache_timestamp).seconds < self.cache_duration and 
                self.menu_cache):
                return self.menu_cache.get('menu_text', '')

            # Determine the current menu type based on time
            hour = current_time.hour
            day = current_time.strftime('%A')
            
            if hour < 11:  # Before 11 AM
                menu_type = 'Breakfast'
            elif hour < 15:  # 11 AM to 3 PM
                menu_type = 'Lunch'
            else:  # After 3 PM
                menu_type = 'Dinner'

            # Add special handling for weekends
            is_weekend = day in ['Saturday', 'Sunday']
            
            menu_text = f"Current {menu_type} Menu ({day}):\n"
            menu_text += self._get_menu_items(menu_type, is_weekend)
            
            # Cache the menu
            self.menu_cache = {
                'menu_text': menu_text,
                'menu_type': menu_type,
                'is_weekend': is_weekend
            }
            self.menu_cache_timestamp = current_time
            
            return menu_text
            
        except Exception as e:
            logger.error(f"Error getting current menu: {str(e)}")
            return "Menu temporarily unavailable"

    def _get_menu_items(self, menu_type, is_weekend):
        """Get menu items based on menu type and whether it's a weekend"""
        # This would typically pull from a database or API
        # For now, using a simplified static menu
        menu_items = {
            'Breakfast': [
                'Farm Fresh Eggs (R65)',
                'Eggs Benedict (R85)',
                'French Toast (R75)',
                'Granola Bowl (R65)'
            ],
            'Lunch': [
                'Caesar Salad (R85)',
                'Gourmet Burger (R125)',
                'Grilled Chicken Sandwich (R95)',
                'Pasta of the Day (R110)'
            ],
            'Dinner': [
                'Grilled Ribeye Steak (R245)',
                'Fresh Line Fish (R195)',
                'Roasted Chicken (R165)',
                'Vegetarian Risotto (R145)'
            ]
        }
        
        # Add weekend specials
        if is_weekend:
            if menu_type == 'Breakfast':
                menu_items[menu_type].append('Weekend Brunch Platter (R145)')
            elif menu_type == 'Lunch':
                menu_items[menu_type].append('Sunday Roast (R185)')
            elif menu_type == 'Dinner':
                menu_items[menu_type].append('Chef\'s Weekend Special (R265)')
        
        return '\n'.join(menu_items.get(menu_type, []))

    def validate_and_correct_response(self, response):
        """Validate and correct any menu-related information in the response"""
        try:
            current_menu = self.get_current_menu()
            
            # Extract menu items and prices
            menu_items = {}
            for line in current_menu.split('\n'):
                if '(R' in line:
                    item_name = line.split('(R')[0].strip()
                    price = 'R' + line.split('(R')[1].rstrip(')')
                    menu_items[item_name.lower()] = price
            
            # Check response for menu items and prices
            corrected_response = response
            for item_name, price in menu_items.items():
                # Look for mentions of menu items without prices
                if item_name in corrected_response.lower() and price not in corrected_response:
                    corrected_response = corrected_response.replace(
                        item_name.title(),
                        f"{item_name.title()} ({price})"
                    )
            
            return corrected_response
            
        except Exception as e:
            logger.error(f"Error validating response: {str(e)}")
            return response  # Return original response if validation fails