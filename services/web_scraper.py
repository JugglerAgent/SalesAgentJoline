import logging
import os
import requests
import tempfile
from pdfreader import PDFDocument, SimplePDFViewer
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class ZevenwachtScraper:
    def __init__(self):
        self.menu_url = "https://zevenwacht.co.za/wp-content/uploads/2025/02/Zevenwacht_Summer_Menu_2025.pdf"
        self.current_section = None
        self.menu_sections = []
        self.current_items = []

    def fetch_menu_pdf(self) -> Optional[str]:
        """Fetch the menu PDF from the restaurant's website."""
        try:
            logger.info(f"Attempting to fetch menu PDF from {self.menu_url}")
            response = requests.get(self.menu_url)
            response.raise_for_status()
            
            # Save PDF to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name
            
            logger.info("Successfully downloaded menu PDF")
            return temp_path
        except Exception as e:
            logger.error(f"Error downloading menu PDF: {str(e)}")
            return None

    def _is_section_header(self, text: str) -> bool:
        """Check if the text is a menu section header."""
        text = text.strip().upper()
        known_sections = [
            "BREAD BOARD", "SMALL PLATES", "MAINS", "GRILLS",
            "SEAFOOD", "BURGERS", "SALADS", "DESSERT"
        ]
        return any(section in text for section in known_sections)

    def _process_menu_item(self, lines: List[str]) -> Dict:
        """Process menu item text to extract name, description, and price."""
        item = {
            "name": "",
            "description": "",
            "price": ""
        }
        
        for line in lines:
            if "R" in line and any(c.isdigit() for c in line):
                # Extract price
                price_parts = line.split("R")
                if len(price_parts) > 1:
                    item["price"] = f"R{price_parts[-1].strip()}"
                    # The rest might be part of the description
                    desc_part = "R".join(price_parts[:-1]).strip()
                    if desc_part:
                        item["description"] = desc_part
            elif not item["name"]:
                item["name"] = line.strip()
            else:
                if item["description"]:
                    item["description"] += " " + line.strip()
                else:
                    item["description"] = line.strip()
        
        return item

    def parse_menu_pdf(self, pdf_path: str) -> List[Dict]:
        """Parse the menu PDF using pdfreader."""
        try:
            logger.info("Starting PDF parsing process")
            with open(pdf_path, 'rb') as file:
                doc = PDFDocument(file)
                viewer = SimplePDFViewer(file)
                
                logger.info(f"Successfully opened PDF with {len(doc.pages)} pages")
                
                current_section = None
                current_item_lines = []
                
                for page_num, _ in enumerate(doc.pages, 1):
                    logger.info(f"Processing page {page_num}")
                    viewer.navigate(page_num)
                    viewer.render()
                    
                    for text in viewer.canvas.strings:
                        text = text.strip()
                        if not text:
                            continue
                            
                        if self._is_section_header(text):
                            # Process previous item if exists
                            if current_item_lines:
                                if current_section:
                                    item = self._process_menu_item(current_item_lines)
                                    self.menu_sections.append({
                                        "name": current_section,
                                        "items": [item]
                                    })
                                current_item_lines = []
                            
                            current_section = text
                            logger.info(f"Found new section: {current_section}")
                        else:
                            current_item_lines.append(text)
                    
                    # Process last item of the page
                    if current_item_lines and current_section:
                        item = self._process_menu_item(current_item_lines)
                        self.menu_sections.append({
                            "name": current_section,
                            "items": [item]
                        })
                        current_item_lines = []
                
                logger.info(f"Completed menu parsing with {len(self.menu_sections)} sections")
                return self.menu_sections
                
        except Exception as e:
            logger.error(f"Error parsing menu PDF: {str(e)}")
            logger.error(f"Traceback: {str(e.__traceback__)}")
            return []
        finally:
            # Clean up temporary file
            if os.path.exists(pdf_path):
                os.remove(pdf_path)