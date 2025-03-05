import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from services.web_scraper import ZevenwachtScraper
from models.product import Product

class ZevenwachtPicnicScraper(ZevenwachtScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://zevenwacht.co.za/picnics/"
        self.logger = logging.getLogger(__name__)

    def parse_picnic_info(self, html_content):
        if not html_content:
            return None

        soup = BeautifulSoup(html_content, 'html.parser')
        picnic_data = {
            'last_updated': datetime.now().isoformat(),
            'packages': []
        }

        try:
            main_content = soup.find('main', {'id': 'main'})
            if main_content:
                # Find all picnic package sections
                package_sections = main_content.find_all(['section', 'div'], class_=['picnic-package', 'package-details'])
                
                for section in package_sections:
                    package = {
                        'name': '',
                        'description': '',
                        'price': '',
                        'features': [],
                        'specifications': {}
                    }

                    # Extract package name
                    name_elem = section.find(['h2', 'h3'])
                    if name_elem:
                        package['name'] = name_elem.get_text(strip=True)

                    # Extract description
                    desc_elem = section.find('p', class_=['description', 'package-description'])
                    if desc_elem:
                        package['description'] = desc_elem.get_text(strip=True)

                    # Extract price
                    price_elem = section.find(['span', 'div'], class_=['price', 'package-price'])
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        # Extract numeric price value
                        import re
                        price_match = re.search(r'R\s*(\d+(?:\.\d{2})?)', price_text)
                        if price_match:
                            package['price'] = float(price_match.group(1))

                    # Extract features
                    features_list = section.find_all(['li', 'div'], class_=['feature', 'package-feature'])
                    for feature in features_list:
                        feature_text = feature.get_text(strip=True)
                        if feature_text:
                            package['features'].append(feature_text)

                    # Extract specifications
                    specs = {
                        'availability': 'All year round',  # Default value
                        'booking_required': 'Yes',
                        'category': 'Picnic'
                    }

                    # Look for specific availability information
                    availability_elem = section.find(text=re.compile(r'available|seasonal', re.I))
                    if availability_elem:
                        specs['availability'] = availability_elem.strip()

                    package['specifications'] = specs
                    picnic_data['packages'].append(package)

        except Exception as e:
            self.logger.error(f"Error parsing picnic information: {str(e)}")
            return None

        return picnic_data

    def update_knowledge_base(self, knowledge_base):
        """Update the knowledge base with picnic information"""
        html_content = self.fetch_page()
        if html_content:
            picnic_data = self.parse_picnic_info(html_content)
            if picnic_data and picnic_data['packages']:
                for package in picnic_data['packages']:
                    picnic_product = Product(
                        name=package['name'],
                        description=package['description'],
                        price=package['price'],
                        features=package['features'],
                        specifications=package['specifications']
                    )
                    knowledge_base.add_product(picnic_product)
                return True
        return False