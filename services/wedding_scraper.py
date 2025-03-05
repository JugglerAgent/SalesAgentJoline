import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from services.web_scraper import ZevenwachtScraper
from models.product import Product

class ZevenwachtWeddingScraper(ZevenwachtScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://zevenwacht.co.za/weddings/"
        self.logger = logging.getLogger(__name__)
        self.contact_info = {
            'email': 'restaurant@zevenwacht.co.za',
            'phone': None,  # Will be extracted from the website
            'inquiry_message': 'For detailed wedding information and customized packages, please contact us directly.'
        }

    def parse_wedding_info(self, html_content):
        if not html_content:
            return None

        soup = BeautifulSoup(html_content, 'html.parser')
        wedding_data = {
            'last_updated': datetime.now().isoformat(),
            'packages': [],
            'contact_info': self.contact_info.copy()
        }

        try:
            main_content = soup.find('main', {'id': 'main'})
            if main_content:
                # Extract contact information if available
                contact_section = main_content.find(['div', 'section'], class_=['contact-info', 'contact-details'])
                if contact_section:
                    phone_elem = contact_section.find('a', href=lambda x: x and 'tel:' in x)
                    if phone_elem:
                        wedding_data['contact_info']['phone'] = phone_elem.get_text(strip=True)

                # Find all wedding package sections
                package_sections = main_content.find_all(['section', 'div'], class_=['wedding-package', 'venue-package'])
                
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

                    # Extract basic description
                    desc_elem = section.find('p', class_=['description', 'package-description'])
                    if desc_elem:
                        package['description'] = desc_elem.get_text(strip=True)

                    # Extract basic features
                    features_list = section.find_all(['li', 'div'], class_=['feature', 'package-feature'])
                    for feature in features_list[:5]:  # Limit to 5 basic features
                        feature_text = feature.get_text(strip=True)
                        if feature_text:
                            package['features'].append(feature_text)

                    # Add basic specifications
                    package['specifications'] = {
                        'category': 'Wedding',
                        'contact_for_pricing': True,
                        'booking_required': 'Yes'
                    }

                    wedding_data['packages'].append(package)

        except Exception as e:
            self.logger.error(f"Error parsing wedding information: {str(e)}")
            return None

        return wedding_data

    def update_knowledge_base(self, knowledge_base):
        """Update the knowledge base with basic wedding information"""
        html_content = self.fetch_page()
        if html_content:
            wedding_data = self.parse_wedding_info(html_content)
            if wedding_data and wedding_data['packages']:
                for package in wedding_data['packages']:
                    wedding_product = Product(
                        name=package['name'],
                        description=package['description'],
                        price='Contact for pricing',
                        features=package['features'],
                        specifications=package['specifications']
                    )
                    knowledge_base.add_product(wedding_product)
                return True
        return False