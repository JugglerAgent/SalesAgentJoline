from services.knowledge_base import KnowledgeBase
import logging

logger = logging.getLogger(__name__)
import logging

logger = logging.getLogger(__name__)
import logging

logger = logging.getLogger(__name__)
from config.restaurant_config import RestaurantConfig
from models.product import Product
import json

class RestaurantKnowledgeBase(KnowledgeBase):
    def __init__(self):
        super().__init__()
        self._initialize_menu_items()
        self._initialize_venue_packages()

    def _initialize_menu_items(self):
        """Initialize and structure menu data from restaurant_data.json for AI integration"""
        try:
            with open('restaurant_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Create structured data format for AI processing
            structured_data = {
                "restaurant_name": data["name"],
                "menu_sections": [],
                "all_items": [],
                "last_updated": data.get("last_updated", "")
            }

            # Process all menu sections
            for section in data.get("menu_sections", []):
                section_entry = {
                    "section_name": section["name"],
                    "serving_hours": section.get("serving_hours", "All day"),
                    "items": []
                }
                
                for item in section.get("items", []):
                    item_entry = {
                        "name": item["name"],
                        "description": item.get("description", ""),
                        "price": item.get("price"),
                        "category": section["name"],
                        "allergens": item.get("allergens", []),
                        "dietary": item.get("dietary", [])
                    }
                    section_entry["items"].append(item_entry)
                    structured_data["all_items"].append(item_entry)
                
                structured_data["menu_sections"].append(section_entry)

            # Add structured data to knowledge base
            self.add_structured_data('menu', structured_data)
            
            # Create Product entries for querying
            for item in structured_data["all_items"]:
                self.add_product(Product(
                    name=item["name"],
                    description=item.get("description", ""),
                    price=item.get("price"),
                    specifications={
                        'category': item["category"],
                        'serving_hours': item.get("serving_hours", ""),
                        'allergens': item.get("allergens", []),
                        'dietary': item.get("dietary", [])
                    }
                ))

            logger.info(f"Successfully loaded menu data with {len(structured_data['all_items'])} items")

        except Exception as e:
            logger.error(f"Failed to initialize menu data: {str(e)}")
            raise

    def explain_market_price(self, item_name):
        """Provide explanation for items with market pricing"""
        product = self.get_product_by_name(item_name)
        if product and product.specifications.get('market_price'):
            return f"The price for {item_name} varies based on market conditions and daily availability. Please ask our staff for today's current price."
        return None

    def _initialize_venue_packages(self):
        """Initialize venue packages from RestaurantConfig"""
        for package_type, package in RestaurantConfig.VENUE_PACKAGES.items():
            venue_package = Product(
                name=package['name'],
                description=f"Capacity: {package['capacity']}",
                price=package['base_price'],
                features=package['features'],
                specifications={
                    'type': package_type,
                    'peak_season': package.get('peak_season', 'N/A'),
                    'availability': package.get('availability', 'All days'),
                    'minimum_spend': package.get('minimum_spend', 'N/A')
                }
            )
            self.add_product(venue_package)

    def get_restaurant_context(self):
        """Generate a comprehensive context string about the restaurant"""
        context = "Restaurant Information:\n\n"

        # Operating Hours
        context += "Operating Hours:\n"
        for day, hours in RestaurantConfig.OPERATING_HOURS.items():
            context += f"{day}: {hours}\n"

        # Location
        context += "\nLocation:\n"
        for key, value in RestaurantConfig.LOCATION.items():
            context += f"{key.replace('_', ' ').title()}: {value}\n"

        # Booking Policies
        context += "\nBooking Policies:\n"
        policies = RestaurantConfig.BOOKING_POLICIES
        context += f"- Reservation required: {'Yes' if policies['reservation_required'] else 'No'}\n"
        context += f"- Group size: {policies['minimum_group_size']}-{policies['maximum_group_size']} people\n"
        context += f"- Cancellation policy: {policies['cancellation_policy']}\n"

        # Products (Menu Items and Venue Packages)
        context += "\n" + self.get_product_context()

        return context

    def get_dietary_options(self, requirement):
        """Get menu items suitable for specific dietary requirements"""
        suitable_items = []
        for product in self.get_all_products():
            dietary = product.specifications.get('dietary', '')
            if requirement.lower() in dietary.lower():
                suitable_items.append(product)
        return suitable_items

    def get_menu_by_category(self, category):
        """Get all menu items in a specific category"""
        return [product for product in self.get_all_products()
                if product.specifications.get('category') == category]

    def get_venue_packages(self):
        """Get all venue packages"""
        return [product for product in self.get_all_products()
                if 'type' in product.specifications]
                
    def update_restaurant_info(self, restaurant_info):
        """Update restaurant information in the knowledge base"""
        try:
            # Add structured data to knowledge base
            self.add_structured_data('restaurant_info', restaurant_info)
            logger.info(f"Successfully updated restaurant information")
            return True
        except Exception as e:
            logger.error(f"Failed to update restaurant information: {str(e)}")
            return False
            
    def update_menu(self, menu_type, items):
        """Update a specific menu in the knowledge base"""
        try:
            # Add structured data to knowledge base
            self.add_structured_data(f'menu_{menu_type}', items)
            logger.info(f"Successfully updated {menu_type} menu")
            return True
        except Exception as e:
            logger.error(f"Failed to update {menu_type} menu: {str(e)}")
            return False
            
    def update_specials(self, specials):
        """Update specials in the knowledge base"""
        try:
            # Add structured data to knowledge base
            self.add_structured_data('specials', specials)
            logger.info(f"Successfully updated specials")
            return True
        except Exception as e:
            logger.error(f"Failed to update specials: {str(e)}")
            return False