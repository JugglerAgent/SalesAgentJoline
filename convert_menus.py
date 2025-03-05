import os
import pdfkit
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_menus():
    """Convert all HTML menus to PDF"""
    attachments_dir = 'attachments'
    menu_files = [
        'breakfast_menu',
        'kiddies_menu',
        'a_la_carte_menu',
        'wine_list',
        'drinks_menu'
    ]

    config = pdfkit.configuration(wkhtmltopdf=r'wkhtmltopdf.exe')
    options = {
        'quiet': '',
        'enable-local-file-access': None
    }

    for menu in menu_files:
        html_path = os.path.join(attachments_dir, f'{menu}.html')
        pdf_path = os.path.join(attachments_dir, f'{menu}.pdf')

        if os.path.exists(html_path) and not os.path.exists(pdf_path):
            try:
                logger.info(f"Converting {menu} to PDF...")
                pdfkit.from_file(html_path, pdf_path, options=options, configuration=config)
                logger.info(f"Successfully converted {menu} to PDF")
            except Exception as e:
                logger.error(f"Error converting {menu} to PDF: {str(e)}")

if __name__ == "__main__":
    convert_menus()