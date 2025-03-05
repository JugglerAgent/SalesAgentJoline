import os
import json
from datetime import datetime

class MenuHtmlGenerator:
    """
    A class to generate HTML menu files from the restaurant data.
    This is used to update the HTML menu files when the menu data is updated through the training interface.
    """
    
    def __init__(self, restaurant_data_path="restaurant_data.json"):
        self.restaurant_data_path = restaurant_data_path
        self.attachments_dir = "attachments"
        self.menu_mapping = {
            "BREAKFAST MENU": "breakfast_menu.html",
            "MAINS": "a_la_carte_menu.html",
            "GRILLS": "a_la_carte_menu.html",
            "SEAFOOD": "a_la_carte_menu.html",
            "SALADS": "a_la_carte_menu.html",
            "SMALL PLATES": "a_la_carte_menu.html",
            "BREAD BOARD": "a_la_carte_menu.html",
            "DESSERT": "a_la_carte_menu.html",
            "KIDDIES MENU": "kiddies_menu.html",
            "BEVERAGES": "drinks_menu.html",
            "WINE SECTIONS": "wine_list.html"
        }
        self.menu_titles = {
            "breakfast_menu.html": "Breakfast Menu",
            "a_la_carte_menu.html": "À La Carte Menu",
            "kiddies_menu.html": "Kiddies Menu",
            "drinks_menu.html": "Drinks Menu",
            "wine_list.html": "Wine List"
        }
        self.menu_sections = {
            "breakfast_menu.html": ["BREAKFAST MENU", "BREAKFAST DRINKS"],
            "a_la_carte_menu.html": ["BREAD BOARD", "SMALL PLATES", "MAINS", "GRILLS", "SEAFOOD", "SALADS", "DESSERT"],
            "kiddies_menu.html": ["KIDDIES MENU"],
            "drinks_menu.html": ["BEVERAGES"],
            "wine_list.html": ["WINE SECTIONS"]
        }
    
    def load_restaurant_data(self):
        """Load the restaurant data from the JSON file."""
        try:
            with open(self.restaurant_data_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading restaurant data: {str(e)}")
            return None
    
    def generate_all_menus(self):
        """Generate all HTML menu files."""
        restaurant_data = self.load_restaurant_data()
        if not restaurant_data:
            return False
        
        # Generate each menu file
        for menu_file in self.menu_titles.keys():
            self.generate_menu_file(restaurant_data, menu_file)
        
        return True
    
    def generate_menu_file(self, restaurant_data, menu_file):
        """Generate a specific HTML menu file."""
        menu_title = self.menu_titles.get(menu_file, "Menu")
        menu_sections_to_include = self.menu_sections.get(menu_file, [])
        
        # Get the sections for this menu
        sections_html = ""
        for section_name in menu_sections_to_include:
            section = self._find_section(restaurant_data, section_name)
            if section:
                sections_html += self._generate_section_html(section)
        
        # Generate the full HTML
        html = self._generate_menu_html(menu_title, sections_html)
        
        # Write the HTML to the file
        file_path = os.path.join(self.attachments_dir, menu_file)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(html)
        
        print(f"Generated {menu_file}")
    
    def _find_section(self, restaurant_data, section_name):
        """Find a section in the restaurant data by name."""
        for section in restaurant_data.get("menu_sections", []):
            if section["name"].upper() == section_name.upper():
                return section
        return None
    
    def _generate_section_html(self, section):
        """Generate HTML for a menu section."""
        section_html = f"""
    <div class="section">
        <div class="section-title">{section["name"]}</div>
"""
        
        # Handle regular items
        for item in section.get("items", []):
            if "items" in item:
                # This is a subsection (like in wine sections)
                section_html += f"""
        <div class="subsection">
            <div class="subsection-title">{item["name"]}</div>
"""
                for subitem in item.get("items", []):
                    section_html += self._generate_item_html(subitem)
                
                section_html += """
        </div>
"""
            else:
                # This is a regular item
                section_html += self._generate_item_html(item)
        
        section_html += """
    </div>
"""
        return section_html
    
    def _generate_item_html(self, item):
        """Generate HTML for a menu item."""
        name = item.get("name", "")
        description = item.get("description", "")
        
        # Handle different price formats
        price_html = ""
        if "price" in item:
            if item["price"] is None:
                price_html = "Market Price"
            else:
                # Ensure we don't add an extra 'R' if the price already has one
                price_str = str(item["price"])
                if price_str.startswith('R'):
                    price_html = price_str
                else:
                    price_html = f"R{price_str}"
        elif "price_glass" in item and "price_bottle" in item:
            price_html = f"R{item['price_glass']} (glass) / R{item['price_bottle']} (bottle)"
        
        return f"""
        <div class="item">
            <div class="item-name">{name}</div>
            <div class="item-description">{description}</div>
            <div class="item-price">{price_html}</div>
        </div>
"""
    
    def _generate_menu_html(self, title, sections_html):
        """Generate the full HTML for a menu."""
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Zevenwacht Restaurant - {title}</title>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
            background-color: #fff;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #722f37;
            padding-bottom: 20px;
        }}
        .logo {{
            font-size: 28px;
            font-weight: bold;
            color: #722f37;
            margin-bottom: 10px;
        }}
        .subtitle {{
            font-size: 20px;
            color: #666;
            font-style: italic;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section-title {{
            background-color: #722f37;
            color: white;
            padding: 10px 15px;
            margin-bottom: 20px;
            font-size: 18px;
            font-weight: bold;
        }}
        .subsection {{
            margin-bottom: 30px;
        }}
        .subsection-title {{
            color: #722f37;
            font-weight: bold;
            font-size: 16px;
            margin-bottom: 15px;
            border-bottom: 1px solid #722f37;
            padding-bottom: 5px;
        }}
        .item {{
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #eee;
        }}
        .item-name {{
            font-weight: bold;
            color: #722f37;
            font-size: 16px;
            margin-bottom: 5px;
        }}
        .item-description {{
            font-style: italic;
            color: #666;
            margin: 5px 0;
            line-height: 1.4;
        }}
        .item-price {{
            color: #722f37;
            font-weight: bold;
            margin-top: 5px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #722f37;
            font-size: 14px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">ZEVENWACHT RESTAURANT</div>
        <div class="subtitle">{title}</div>
        <p>Zeevenwacht Wine Estate, Langverwacht Rd, Kuils River</p>
        <p>Main Service Hours: Tuesday-Sunday, 12:00-22:00 (Last orders at 21:00)</p>
    </div>

{sections_html}

    <div class="footer">
        <p>All prices include VAT</p>
        <p>Please inform your server of any dietary requirements or allergies</p>
        <p>A 10% service charge will be added to tables of 8 or more</p>
        <p>Contact: jolinesalesagent@gmail.com | Tel: +27 (21) 903 5123</p>
        <p>Last updated: {datetime.now().strftime("%d %B %Y")}</p>
    </div>
</body>
</html>"""