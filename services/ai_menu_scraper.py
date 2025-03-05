import logging
import requests
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
import os
import PyPDF2
from io import BytesIO

load_dotenv()

class AIMenuScraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://api.openai.com/v1"
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            self.logger.error("OPENAI_API_KEY not found in .env file")
            raise ValueError("OPENAI_API_KEY not found")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _is_section_header(self, text: str) -> bool:
        """Determine if a line of text is a menu section header."""
        # Convert to uppercase for consistent comparison
        text = text.upper()
        
        # Common section header patterns
        section_patterns = [
            r'^[A-Z\s]{3,}$',  # All caps with spaces
            r'^[A-Z][A-Z\s]*S$',  # Ends with S (e.g., MAINS, GRILLS)
            r'^THE\s+[A-Z\s]+$',  # Starts with THE
            r'^[A-Z]+\s+[A-Z]+$',  # Two or more capitalized words
            r'^[A-Z]\s*[A-Z]\s*[A-Z]\s*[A-Z]\s*[A-Z]\s*S$'  # Spaced letters ending in S
        ]
        
        # Known section headers from the menu
        known_sections = {
            'BREAD BOARD', 'SMALL PLATES', 'GRILLS', 'SEAFOOD',
            'BURGERS', 'SALADS', 'DESSERT', 'MAINS', 'STARTERS'
        }
        
        # Check if text matches any known section
        if text.strip() in known_sections:
            return True
            
        # Check if text matches any pattern
        return any(re.match(pattern, text.strip()) for pattern in section_patterns)

    def extract_menu_from_pdf(self, pdf_content: bytes) -> Optional[Dict]:
        """Extract menu information from PDF using OpenAI's GPT model."""
        try:
            # Extract text from PDF locally
            pdf = PyPDF2.PdfReader(BytesIO(pdf_content))
            menu_text = ""
            for page in pdf.pages:
                # Extract text with careful handling of line breaks and spacing
                page_text = page.extract_text() or ""
                # Process text line by line
                lines = []
                current_item = ""
                for line in page_text.split('\n'):
                    # Fix unwanted spaces in words (e.g., "SM OKED" -> "SMOKED")
                    line = re.sub(r'(?<=[A-Z])\s+(?=[A-Z])', '', line)
                    # Clean up spaces while preserving structure
                    line = ' '.join(part for part in line.split() if part)
                    if line:
                        # Extract all prices from the line
                        price_pattern = r'R?\s*\d+(?:\.\d{2})?'
                        prices = re.finditer(price_pattern, line)
                        price_positions = [(m.start(), m.end()) for m in prices]
                        
                        if price_positions:
                            # Split line at price positions
                            last_end = 0
                            for start, end in price_positions:
                                # Add text before price if exists
                                text_before = line[last_end:start].strip()
                                if text_before:
                                    if current_item:
                                        lines.append(current_item.strip())
                                    current_item = text_before
                                
                                # Add price as separate line
                                price = line[start:end]
                                price = re.sub(r'R?\s*(\d+(?:\.\d{2})?)', r'R \1', price)
                                if current_item:
                                    lines.append(current_item.strip())
                                    lines.append(price)
                                    current_item = ""
                                else:
                                    lines.append(price)
                                
                                last_end = end
                            
                            # Add remaining text after last price
                            remaining_text = line[last_end:].strip()
                            if remaining_text:
                                current_item = remaining_text
                        else:
                            # Accumulate non-price lines as potential description
                            current_item += " " + line
                # Add any remaining description
                if current_item:
                    lines.append(current_item.strip())
                # Join lines with proper spacing
                menu_text += '\n'.join(lines) + "\n\n"

            if not menu_text:
                self.logger.error("No text extracted from PDF")
                return None

            # Prepare the prompt
            system_prompt = """
            You are a menu parsing expert for a South African restaurant. Analyze the provided menu text and extract:
            1. Menu sections
            2. Items in each section with:
               - Name (preserve exact formatting)
               - Description (maintain proper spacing and line breaks)
               - Price (format as South African Rand with 'R' prefix)
               - Dietary information
               - Allergens
            
            Important guidelines:
            - Process text thoroughly and maintain proper spacing
            - Ensure prices are in South African Rand (R) format
            - Preserve line breaks and formatting in descriptions
            - Handle special characters carefully
            - Take time to thoroughly analyze each section
            
            Format the output as a structured JSON with the following schema:
            {
                "sections": [{
                    "name": "string",
                    "items": [{
                        "name": "string",
                        "description": "string",
                        "price": "string",
                        "allergens": ["string"],
                        "dietary": ["string"]
                    }]
                }]
            }
            
            Note: Ensure all prices start with 'R' for South African Rand.
            """

            payload = {
                "model": "gpt-4",  # Using GPT-4 for better menu parsing
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Parse this menu:\n{menu_text}"}
                ],
                "temperature": 0.1,
                "max_tokens": 2000
            }

            self.logger.info("Making API call to OpenAI for menu extraction")
            self.logger.info(f"Sending payload: {json.dumps(payload, indent=2)}")
            # Increase timeout and add retries for API call with exponential backoff
            max_retries = 3
            base_timeout = 60
            for attempt in range(max_retries):
                try:
                    timeout = base_timeout * (2 ** attempt)  # Exponential backoff
                    self.logger.info(f"Attempt {attempt + 1} with timeout {timeout} seconds")
                    response = requests.post(
                        f"{self.base_url}/chat/completions",
                        headers=self.headers,
                        json=payload,
                        timeout=timeout
                    )
                    response.raise_for_status()
                    break  # If successful, break the retry loop
                except requests.exceptions.Timeout:
                    if attempt == max_retries - 1:  # Last attempt
                        self.logger.error(f"All {max_retries} attempts timed out")
                        raise
                    self.logger.warning(f"Attempt {attempt + 1} timed out after {timeout} seconds, retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff delay
                    continue
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:  # Last attempt
                        self.logger.error(f"All {max_retries} attempts failed with error: {str(e)}")
                        raise
                    self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}, retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff delay
                    continue
            response.raise_for_status()

            # Process the AI response
            ai_response = response.json()
            if 'choices' not in ai_response or not ai_response['choices']:
                self.logger.error("Invalid response format from OpenAI API")
                return None

            try:
                menu_data = json.loads(ai_response['choices'][0]['message']['content'])
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse AI response as JSON: {str(e)}")
                return None

            if 'sections' not in menu_data:
                self.logger.error("AI response missing required 'sections' field")
                return None

            # Format the final restaurant data
            restaurant_data = {
                'last_updated': datetime.now().isoformat(),
                'name': 'Zevenwacht Restaurant',
                'menu_sections': []
            }

            # Process and validate the AI-extracted menu data
            for section in menu_data['sections']:
                if not isinstance(section, dict) or 'name' not in section or 'items' not in section:
                    self.logger.warning(f"Skipping invalid section format: {section}")
                    continue

                menu_section = {
                    'name': section['name'].upper().strip(),
                    'items': []
                }

                for item in section['items']:
                    if not isinstance(item, dict) or 'name' not in item:
                        self.logger.warning(f"Skipping invalid menu item format: {item}")
                        continue

                    # Clean up item name and ensure it's complete
                    item_name = item['name'].strip()
                    if item_name.endswith('BURGE'):
                        item_name = item_name + 'R'

                    menu_item = {
                        'name': item_name.upper(),
                        'description': item.get('description', '').strip(),
                        'price': item.get('price', '').strip(),
                        'allergens': [a.strip() for a in item.get('allergens', [])],
                        'dietary': [d.strip() for d in item.get('dietary', [])]
                    }
                    menu_section['items'].append(menu_item)

                restaurant_data['menu_sections'].append(menu_section)

            if not restaurant_data['menu_sections']:
                self.logger.error("No valid menu sections extracted")
                return None

            self.logger.info(f"Successfully extracted {len(restaurant_data['menu_sections'])} menu sections")
            return restaurant_data

        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error extracting menu data: {str(e)}")
            return None

    def update_restaurant_data(self, pdf_url: str) -> bool:
        """Update restaurant data by downloading and processing the menu PDF."""
        if not pdf_url or not pdf_url.startswith('http'):
            self.logger.error("Invalid PDF URL provided")
            return False

        try:
            # Download PDF
            self.logger.info(f"Downloading PDF from {pdf_url}")
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            pdf_content = response.content

            # Extract menu data
            self.logger.info("Extracting menu data from PDF")
            restaurant_data = self.extract_menu_from_pdf(pdf_content)
            if not restaurant_data:
                return False

            # Save to JSON file
            self.logger.info("Saving extracted menu data to JSON file")
            with open('restaurant_data.json', 'w', encoding='utf-8') as f:
                json.dump(restaurant_data, f, indent=4, ensure_ascii=False)

            self.logger.info("Restaurant data successfully updated")
            return True

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to download PDF: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Error updating restaurant data: {str(e)}")
            return False