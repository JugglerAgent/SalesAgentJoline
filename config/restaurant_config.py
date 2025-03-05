class RestaurantConfig:
    @staticmethod
    def load_menu_data():
        """Load menu data from the scraped JSON file"""
        import json
        try:
            with open('restaurant_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'menu_sections' in data:
                    menu_categories = {}
                    for section in data['menu_sections']:
                        category_name = section['name'].lower()
                        menu_items = []
                        for item in section['items']:
                            menu_item = {
                                'name': item['name'],
                                'description': item.get('description', ''),
                                'price': item.get('price'),
                                'allergens': item.get('allergens', []),
                                'dietary': item.get('dietary', [])
                            }
                            menu_items.append(menu_item)
                        menu_categories[category_name] = menu_items
                    return menu_categories
                return {}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    # À La Carte Menu Information
    MENU_CATEGORIES = load_menu_data()


    # Venue Hire Information
    VENUE_PACKAGES = {
        'wedding': {
            'name': 'Wedding Package',
            'capacity': '20-150 guests',
            'features': [
                'Exclusive use of the main restaurant',
                'Outdoor ceremony area',
                'Wine tasting experience',
                'Customizable menu options'
            ],
            'base_price': 'From R25,000',
            'peak_season': 'October-April'
        },
        'corporate': {
            'name': 'Corporate Package',
            'capacity': '10-50 guests',
            'features': [
                'Private dining room',
                'AV equipment',
                'Team building activities',
                'Wine tasting options'
            ],
            'base_price': 'From R15,000',
            'peak_season': 'All year'
        }
    }

    # General Information
    OPERATING_HOURS = {
        'Monday': 'Closed',
        'Tuesday-Sunday': {
            'Breakfast': '07:30-11:00',
            'Main Service': '12:00-22:00'
        },
        'Kitchen_last_order': '21:00'
    }

    LOCATION = {
        'address': 'Zeevenwacht Wine Estate, Langverwacht Rd, Kuils River',
        'coordinates': '-33.9277, 18.7219',
        'parking': 'Free secure parking available on premises',
        'directions': 'Located 25 minutes from Cape Town CBD, accessible via N1'
    }

    BOOKING_POLICIES = {
        'reservation_required': True,
        'minimum_group_size': 2,
        'maximum_group_size': 150,
        'deposit_required': {
            'groups_over_8': True,
            'special_events': True
        },
        'cancellation_policy': '48 hours notice required for full refund'
    }

    @classmethod
    def get_menu_item(cls, category, item_name):
        """Retrieve specific menu item details"""
        category_items = cls.MENU_CATEGORIES.get(category, [])
        return next((item for item in category_items if item['name'] == item_name), None)

    @classmethod
    def get_venue_package(cls, package_type):
        """Retrieve specific venue package details"""
        return cls.VENUE_PACKAGES.get(package_type)

    @classmethod
    def is_operating(cls, day):
        """Check if restaurant is operating on specified day"""
        return day.lower() != 'monday'

    @classmethod
    def get_dietary_options(cls, dietary_requirement):
        """Get menu items suitable for specific dietary requirements"""
        suitable_items = []
        for category, items in cls.MENU_CATEGORIES.items():
            for item in items:
                if dietary_requirement in item.get('dietary', []):
                    suitable_items.append(item)
        return suitable_items