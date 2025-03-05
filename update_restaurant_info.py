import schedule
import time
from services.ai_menu_scraper import AIMenuScraper
from services.restaurant_knowledge_base import RestaurantKnowledgeBase
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('restaurant_updates.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def update_restaurant_info():
    logger.info("Starting restaurant information update...")
    restaurant_scraper = AIMenuScraper()
    
    # Create knowledge base instance
    knowledge_base = RestaurantKnowledgeBase()
    
    # Update restaurant information
    pdf_url = "https://zevenwacht.co.za/wp-content/uploads/2025/02/Zevenwacht_Summer_Menu_2025.pdf"
    if restaurant_scraper.update_restaurant_data(pdf_url):
        logger.info("Restaurant information updated successfully")
    else:
        logger.error("Failed to update restaurant information")

def main():
    # Schedule updates to run daily at 1:00 AM
    schedule.every().day.at("01:00").do(update_restaurant_info)
    
    # Run the first update immediately
    update_restaurant_info()
    
    logger.info("Update scheduler started. Press Ctrl+C to exit.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Update scheduler stopped.")

if __name__ == "__main__":
    main()