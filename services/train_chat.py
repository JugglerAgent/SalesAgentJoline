import os
import json
import re
from datetime import datetime
from services.openai_service import OpenAIService
from config.restaurant_config import RestaurantConfig
from services.restaurant_knowledge_base import RestaurantKnowledgeBase
from services.menu_html_generator import MenuHtmlGenerator

class TrainingChat:
    """
    A chat interface for training the Joline AI agent.
    Allows restaurant owners or managers to update restaurant information,
    menu items, prices, specials, etc. through conversation.
    """
    
    def __init__(self):
        self.openai_service = OpenAIService()
        self.restaurant_config = RestaurantConfig()
        self.knowledge_base = RestaurantKnowledgeBase()
        self.restaurant_data_path = "restaurant_data.json"
        self.updates_log_path = "restaurant_updates.log"
        self.menu_html_generator = MenuHtmlGenerator(self.restaurant_data_path)
        self.load_restaurant_data()
        
    def load_restaurant_data(self):
        """Load the current restaurant data from the JSON file."""
        try:
            with open(self.restaurant_data_path, 'r') as file:
                self.restaurant_data = json.load(file)
                
                # Ensure required fields exist
                if "training_history" not in self.restaurant_data:
                    self.restaurant_data["training_history"] = []
                    
                if "specials" not in self.restaurant_data:
                    self.restaurant_data["specials"] = []
                    
                if "restaurant_info" not in self.restaurant_data:
                    self.restaurant_data["restaurant_info"] = {
                        "name": self.restaurant_data.get("name", "Zevenwacht Restaurant"),
                        "address": "Zeevenwacht Wine Estate, Langverwacht Rd, Kuils River",
                        "phone": "+27 21 903 5123",
                        "email": "restaurant@zevenwacht.co.za",
                        "website": "https://www.zevenwacht.co.za"
                    }
                    
        except (FileNotFoundError, json.JSONDecodeError):
            # Initialize with default data if file doesn't exist or is invalid
            self.restaurant_data = {
                "name": "Zevenwacht Restaurant",
                "last_updated": datetime.now().isoformat(),
                "menu_sections": [],
                "specials": [],
                "restaurant_info": {
                    "name": "Zevenwacht Restaurant",
                    "address": "Zeevenwacht Wine Estate, Langverwacht Rd, Kuils River",
                    "phone": "+27 21 903 5123",
                    "email": "restaurant@zevenwacht.co.za",
                    "website": "https://www.zevenwacht.co.za"
                },
                "training_history": []
            }
            self.save_restaurant_data()
    
    def save_restaurant_data(self):
        """Save the updated restaurant data to the JSON file."""
        # Update the last_updated timestamp
        self.restaurant_data["last_updated"] = datetime.now().isoformat()
        
        # Save to JSON file
        with open(self.restaurant_data_path, 'w') as file:
            json.dump(self.restaurant_data, file, indent=4)
        
        # Log the update
        self.log_update("Restaurant data updated")
    
    def log_update(self, message):
        """Log updates to the restaurant information."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        with open(self.updates_log_path, 'a') as file:
            file.write(log_entry)
    
    def has_pending_confirmation(self):
        """Check if there's a pending action that requires confirmation."""
        if not self.restaurant_data.get("training_history"):
            return False
            
        last_message = self.restaurant_data["training_history"][-1]
        return last_message.get("role") == "assistant" and last_message.get("requires_confirmation", False)
    
    def get_pending_action(self):
        """Get the pending action that requires confirmation."""
        if not self.has_pending_confirmation():
            return None
            
        return self.restaurant_data["training_history"][-1].get("pending_action")
    
    def process_confirmation(self, user_message):
        """Process a confirmation message from the user."""
        # Add message to training history
        self.restaurant_data["training_history"].append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Get the pending action first
        pending_action = self.get_pending_action()
        
        if not pending_action:
            # No pending action found
            response = "I'm sorry, there was no pending action to confirm."
            self.restaurant_data["training_history"].append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            return response
        
        # Check if the user confirmed the action
        confirmation_keywords = ["yes", "confirm", "ok", "sure", "proceed", "go ahead", "do it"]
        is_confirmed = any(keyword in user_message.lower() for keyword in confirmation_keywords)
        
        if not is_confirmed:
            # User did not confirm, cancel the action
            response = "Action cancelled. No changes were made."
            self.restaurant_data["training_history"].append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            return response
        
        # User confirmed, process the pending action
        
        # Process the update based on the intent
        if pending_action["intent"] == "menu_item":
            self.update_menu_item(pending_action)
        elif pending_action["intent"] == "price":
            self.update_price(pending_action)
        elif pending_action["intent"] == "special":
            self.update_special(pending_action)
        elif pending_action["intent"] == "restaurant_info":
            self.update_restaurant_info(pending_action)
        
        # Save the updated data
        self.save_restaurant_data()
        
        # Add response to training history
        self.restaurant_data["training_history"].append({
            "role": "assistant",
            "content": pending_action["confirmation_message"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        return pending_action["confirmation_message"]
    
    def process_training_message(self, user_message):
        """
        Process a training message from the restaurant owner or manager.
        Identify the intent and update the restaurant data accordingly.
        """
        # Check if there's a pending action that requires confirmation
        if self.has_pending_confirmation():
            return self.process_confirmation(user_message)
        
        # Add message to training history
        self.restaurant_data["training_history"].append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Analyze the message to determine the training intent
        system_prompt = """
        You are Joline's training assistant. Your job is to help restaurant owners update Joline's knowledge.
        Analyze the user's message and determine what information they want to update.
        Respond with a JSON object containing:
        1. "intent": The type of update (menu_item, price, special, restaurant_info, other)
        2. "action": The specific action (add, update, remove)
        3. "details": Extracted details about the update
        4. "confirmation_message": A message confirming the update that will be shown to the user
        5. "confirmation_required": A boolean indicating whether confirmation is required before making the change
        6. "confirmation_prompt": A message asking for confirmation before making the change
        """
        
        analysis = self.openai_service.chat_completion(
            system_prompt=system_prompt,
            user_message=user_message,
            response_format={"type": "json_object"}
        )
        
        try:
            analysis_data = json.loads(analysis)
            
            # Check if confirmation is required
            if analysis_data.get("confirmation_required", True):
                # Add confirmation prompt to training history
                self.restaurant_data["training_history"].append({
                    "role": "assistant",
                    "content": analysis_data.get("confirmation_prompt", f"Are you sure you want to {analysis_data['action']} this {analysis_data['intent']}? Please confirm."),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "requires_confirmation": True,
                    "pending_action": analysis_data
                })
                
                return analysis_data.get("confirmation_prompt", f"Are you sure you want to {analysis_data['action']} this {analysis_data['intent']}? Please confirm.")
            
            # Process the update based on the intent
            if analysis_data["intent"] == "menu_item":
                self.update_menu_item(analysis_data)
            elif analysis_data["intent"] == "price":
                self.update_price(analysis_data)
            elif analysis_data["intent"] == "special":
                self.update_special(analysis_data)
            elif analysis_data["intent"] == "restaurant_info":
                self.update_restaurant_info(analysis_data)
            
            # Save the updated data
            self.save_restaurant_data()
            
            # Add response to training history
            self.restaurant_data["training_history"].append({
                "role": "assistant",
                "content": analysis_data["confirmation_message"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            return analysis_data["confirmation_message"]
            
        except (json.JSONDecodeError, KeyError) as e:
            error_message = f"I'm sorry, I couldn't process that training request. Error: {str(e)}"
            
            # Add error response to training history
            self.restaurant_data["training_history"].append({
                "role": "assistant",
                "content": error_message,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            return error_message
    
    def update_menu_item(self, analysis_data):
        """Update a menu item based on the analysis data."""
        details = analysis_data["details"]
        menu_type = details.get("menu_type", "MAINS").upper()
        
        # Ensure menu_sections exists
        if "menu_sections" not in self.restaurant_data:
            self.restaurant_data["menu_sections"] = []
        
        # Find the appropriate menu section
        menu_section = None
        for section in self.restaurant_data["menu_sections"]:
            if section["name"].upper() == menu_type:
                menu_section = section
                break
        
        # If menu section doesn't exist, create it
        if menu_section is None:
            menu_section = {
                "name": menu_type,
                "items": []
            }
            self.restaurant_data["menu_sections"].append(menu_section)
        
        if analysis_data["action"] == "add":
            # Add new menu item
            item_name = details.get("name", "")
            
            # Check if the item already exists to avoid duplicates
            item_exists = False
            for item in menu_section["items"]:
                if item.get("name", "").lower() == item_name.lower():
                    item_exists = True
                    break
            
            if not item_exists:
                new_item = {
                    "name": item_name,
                    "description": details.get("description", ""),
                    "price": details.get("price", 0)
                }
                menu_section["items"].append(new_item)
                self.log_update(f"Added new menu item: {new_item['name']} to {menu_type} menu")
            else:
                self.log_update(f"Menu item '{item_name}' already exists in {menu_type} menu")
            
        elif analysis_data["action"] == "update":
            # Update existing menu item
            item_name = details.get("name", "")
            found = False
            
            # First try to find the item in the specified menu section
            for item in menu_section["items"]:
                if item["name"].lower() == item_name.lower():
                    if "new_name" in details:
                        item["name"] = details["new_name"]
                    if "description" in details:
                        item["description"] = details["description"]
                    if "price" in details:
                        item["price"] = details["price"]
                    self.log_update(f"Updated menu item: {item_name} in {menu_type} menu")
                    found = True
                    break
            
            # If not found in the specified section, search all sections
            if not found:
                for section in self.restaurant_data["menu_sections"]:
                    for item in section["items"]:
                        if item["name"].lower() == item_name.lower():
                            if "new_name" in details:
                                item["name"] = details["new_name"]
                            if "description" in details:
                                item["description"] = details["description"]
                            if "price" in details:
                                item["price"] = details["price"]
                            self.log_update(f"Updated menu item: {item_name} in {section['name']} menu")
                            found = True
                            break
                    if found:
                        break
                        
        elif analysis_data["action"] == "remove":
            # Remove menu item
            item_name = details.get("name", "")
            found = False
            
            # First try to remove from the specified menu section
            original_count = len(menu_section["items"])
            menu_section["items"] = [
                item for item in menu_section["items"]
                if item["name"].lower() != item_name.lower()
            ]
            if len(menu_section["items"]) < original_count:
                self.log_update(f"Removed menu item: {item_name} from {menu_type} menu")
                found = True
            
            # If not found in the specified section, search all sections
            if not found:
                for section in self.restaurant_data["menu_sections"]:
                    original_count = len(section["items"])
                    section["items"] = [
                        item for item in section["items"]
                        if item["name"].lower() != item_name.lower()
                    ]
                    if len(section["items"]) < original_count:
                        self.log_update(f"Removed menu item: {item_name} from {section['name']} menu")
                        break
    
    def update_price(self, analysis_data):
        """Update a price for a menu item."""
        details = analysis_data["details"]
        menu_type = details.get("menu_type", "").upper()
        item_name = details.get("name", "")
        new_price = details.get("price", 0)
        price_type = details.get("price_type", "")  # For wine items: "glass" or "bottle"
        
        # Ensure menu_sections exists
        if "menu_sections" not in self.restaurant_data:
            self.restaurant_data["menu_sections"] = []
            return
        
        found = False
        
        # If menu_type is specified, try to find the item in that section first
        if menu_type:
            for section in self.restaurant_data["menu_sections"]:
                if section["name"].upper() == menu_type:
                    # Check regular items
                    for item in section["items"]:
                        if item["name"].lower() == item_name.lower():
                            item["price"] = new_price
                            self.log_update(f"Updated price for {item_name} to {new_price} in {section['name']} menu")
                            found = True
                            return
                    
                    # Check for nested items (like in wine sections)
                    for item in section["items"]:
                        if isinstance(item, dict) and "items" in item:
                            for subitem in item["items"]:
                                if subitem["name"].lower() == item_name.lower():
                                    self._update_item_price(subitem, new_price, price_type, item_name, section["name"])
                                    found = True
                                    return
        
        # If not found or menu_type not specified, search all sections
        if not found:
            # First check regular items
            for section in self.restaurant_data["menu_sections"]:
                for item in section["items"]:
                    if isinstance(item, dict) and "name" in item and item["name"].lower() == item_name.lower():
                        item["price"] = new_price
                        self.log_update(f"Updated price for {item_name} to {new_price} in {section['name']} menu")
                        return
            
            # Then check nested items
            for section in self.restaurant_data["menu_sections"]:
                for item in section["items"]:
                    if isinstance(item, dict) and "items" in item:
                        for subitem in item["items"]:
                            if subitem["name"].lower() == item_name.lower():
                                self._update_item_price(subitem, new_price, price_type, item_name, section["name"])
                                return
    
    def _update_item_price(self, item, new_price, price_type, item_name, section_name):
        """Helper method to update an item's price based on price type."""
        if "price_glass" in item and "price_bottle" in item:
            # For wine items with glass and bottle prices
            if price_type.lower() == "glass":
                item["price_glass"] = new_price
                self.log_update(f"Updated glass price for {item_name} to {new_price} in {section_name} menu")
            elif price_type.lower() == "bottle":
                item["price_bottle"] = new_price
                self.log_update(f"Updated bottle price for {item_name} to {new_price} in {section_name} menu")
            else:
                # Default to updating both if not specified
                item["price_glass"] = new_price
                item["price_bottle"] = new_price * 3  # Typical bottle/glass ratio
                self.log_update(f"Updated prices for {item_name} to {new_price} (glass) and {new_price * 3} (bottle) in {section_name} menu")
        else:
            # Regular item with single price
            item["price"] = new_price
            self.log_update(f"Updated price for {item_name} to {new_price} in {section_name} menu")
    
    def update_special(self, analysis_data):
        """Update specials based on the analysis data."""
        details = analysis_data["details"]
        
        # Ensure specials list exists
        if "specials" not in self.restaurant_data:
            self.restaurant_data["specials"] = []
        
        if analysis_data["action"] == "add":
            # Add new special
            new_special = {
                "name": details.get("name", ""),
                "description": details.get("description", ""),
                "price": details.get("price", 0),
                "start_date": details.get("start_date", ""),
                "end_date": details.get("end_date", "")
            }
            self.restaurant_data["specials"].append(new_special)
            self.log_update(f"Added new special: {new_special['name']}")
            
        elif analysis_data["action"] == "update":
            # Update existing special
            special_name = details.get("name", "")
            for special in self.restaurant_data["specials"]:
                if special["name"].lower() == special_name.lower():
                    if "new_name" in details:
                        special["name"] = details["new_name"]
                    if "description" in details:
                        special["description"] = details["description"]
                    if "price" in details:
                        special["price"] = details["price"]
                    if "start_date" in details:
                        special["start_date"] = details["start_date"]
                    if "end_date" in details:
                        special["end_date"] = details["end_date"]
                    self.log_update(f"Updated special: {special_name}")
                    break
                    
        elif analysis_data["action"] == "remove":
            # Remove special
            special_name = details.get("name", "")
            self.restaurant_data["specials"] = [
                special for special in self.restaurant_data["specials"] 
                if special["name"].lower() != special_name.lower()
            ]
            self.log_update(f"Removed special: {special_name}")
    
    def update_restaurant_info(self, analysis_data):
        """Update restaurant information based on the analysis data."""
        details = analysis_data["details"]
        
        # Ensure restaurant_info exists
        if "restaurant_info" not in self.restaurant_data:
            self.restaurant_data["restaurant_info"] = {}
        
        # Handle the case where details might be a string instead of a dictionary
        if isinstance(details, dict):
            for key, value in details.items():
                self.restaurant_data["restaurant_info"][key] = value
                self.log_update(f"Updated restaurant info: {key} to {value}")
        else:
            # If details is a string, log it and add it as a note
            self.restaurant_data["restaurant_info"]["note"] = details
            self.log_update(f"Added note to restaurant info: {details}")
    
    def get_training_history(self):
        """Get the training history."""
        return self.restaurant_data.get("training_history", [])
    
    def export_restaurant_data(self):
        """Export the restaurant data to be used by the chat agent."""
        try:
            # Update the last_updated timestamp
            self.restaurant_data["last_updated"] = datetime.now().isoformat()
            
            # Save the updated data to the JSON file
            self.save_restaurant_data()
            
            # Update the knowledge base with the latest data
            if "restaurant_info" in self.restaurant_data:
                self.knowledge_base.update_restaurant_info(self.restaurant_data["restaurant_info"])
            
            # Update menu information in the knowledge base
            # This will make the changes available to the chat agent
            try:
                # Reinitialize the knowledge base with the updated menu data
                self.knowledge_base._initialize_menu_items()
                self.log_update("Menu data updated in knowledge base")
            except Exception as menu_error:
                self.log_update(f"Error updating menu data: {str(menu_error)}")
                
            # Generate HTML menu files
            try:
                # Generate all HTML menu files
                self.menu_html_generator.generate_all_menus()
                self.log_update("HTML menu files updated")
            except Exception as html_error:
                self.log_update(f"Error updating HTML menu files: {str(html_error)}")
            
            # Update specials in the knowledge base
            if "specials" in self.restaurant_data:
                try:
                    # Add specials to the knowledge base
                    for special in self.restaurant_data["specials"]:
                        from models.product import Product
                        product = Product(
                            name=special["name"],
                            description=special["description"],
                            price=special["price"],
                            specifications={
                                "type": "special",
                                "start_date": special.get("start_date", ""),
                                "end_date": special.get("end_date", "")
                            }
                        )
                        self.knowledge_base.add_product(product)
                    self.log_update("Specials updated in knowledge base")
                except Exception as special_error:
                    self.log_update(f"Error updating specials: {str(special_error)}")
            
            # Log the export
            self.log_update("Restaurant data exported to knowledge base")
            
            return "Restaurant data exported successfully to the knowledge base. Joline has been updated with the latest information. HTML menu files (a_la_carte_menu.html, breakfast_menu.html, kiddies_menu.html, drinks_menu.html, wine_list.html) have also been updated."
        except Exception as e:
            error_message = f"Failed to export restaurant data: {str(e)}"
            self.log_update(error_message)
            return error_message