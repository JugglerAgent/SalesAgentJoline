import pdfkit
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_menu(html_file, pdf_file):
    try:
        # Configure pdfkit with absolute path to wkhtmltopdf
        config = pdfkit.configuration(wkhtmltopdf='wkhtmltopdf.exe')
        
        # Set options for better conversion
        options = {
            'quiet': '',
            'enable-local-file-access': '',
            'disable-smart-shrinking': '',
            'margin-top': '0',
            'margin-right': '0',
            'margin-bottom': '0',
            'margin-left': '0',
            'encoding': 'UTF-8',
            'no-outline': None
        }
        
        # Convert HTML to PDF
        pdfkit.from_file(
            html_file,
            pdf_file,
            options=options,
            configuration=config
        )
        logger.info(f"Successfully converted {html_file} to PDF")
        return True
    except Exception as e:
        logger.error(f"Error converting {html_file} to PDF: {str(e)}")
        return False

def main():
    attachments_dir = 'attachments'
    menus_to_convert = [
        'breakfast_menu',
        'kiddies_menu'
    ]
    
    for menu in menus_to_convert:
        html_path = os.path.join(attachments_dir, f'{menu}.html')
        pdf_path = os.path.join(attachments_dir, f'{menu}.pdf')
        
        if os.path.exists(html_path) and not os.path.exists(pdf_path):
            logger.info(f"Converting {menu}...")
            convert_menu(html_path, pdf_path)

if __name__ == "__main__":
    main()