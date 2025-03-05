import logging
import json
from services.ai_menu_scraper import AIMenuScraper

logging.basicConfig(level=logging.INFO)

def display_menu():
    try:
        scraper = AIMenuScraper()
        print('Fetching and parsing menu data...')
        pdf_url = "https://zevenwacht.co.za/wp-content/uploads/2025/02/Zevenwacht_Summer_Menu_2025.pdf"
        success = scraper.update_restaurant_data(pdf_url)
        
        if not success:
            print('Failed to fetch and parse menu data')
            return
            
        # Read the parsed menu data from the JSON file
        with open('restaurant_data.json', 'r', encoding='utf-8') as f:
            menu_data = json.load(f)
        
        if not menu_data or 'menu_sections' not in menu_data:
            print('No menu sections found in the parsed data')
            return
            
        print('\nComplete Menu Structure:\n')
        for section in menu_data['menu_sections']:
            print(f"\n{section['name']}")
            print('=' * len(section['name']))
            
            for item in section['items']:
                print(f"\n{item['name']} - {item['price']}")
                if item['description']:
                    print(f"Description: {item['description']}")
                if item['allergens']:
                    print(f"Allergens: {', '.join(item['allergens'])}")
                if item['dietary']:
                    print(f"Dietary: {', '.join(item['dietary'])}")
                print()
                
    except Exception as e:
        print(f'Error: {str(e)}')

if __name__ == '__main__':
    display_menu()