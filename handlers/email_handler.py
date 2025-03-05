from services.openai_service import OpenAIService
from services.knowledge_base import KnowledgeBase
from services.chat_agent import ChatAgent
import smtplib
import os
import pdfkit
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from config.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailHandler:
    def __init__(self):
        self.chat_agent = ChatAgent()
        self.knowledge_base = KnowledgeBase()
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.email_address = Config.EMAIL_ADDRESS
        self.email_password = Config.EMAIL_PASSWORD
        self.attachments_dir = 'attachments'

    def send_email(self, to_email, subject, message, attachments=None):
        msg = MIMEMultipart()
        msg['From'] = self.email_address
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))

        # Add attachments if any
        if attachments:
            for filename, filepath in attachments:
                self._attach_file(msg, filepath, filename)

        try:
            logger.info(f"Attempting to send email to {to_email}")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.send_message(msg)
            server.quit()
            logger.info(f"Successfully sent email to {to_email}")
            return True
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP Authentication failed. Please check your email credentials.")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False

    def _determine_subject(self, content):
        """Determine appropriate subject based on email content"""
        content_lower = content.lower()
        if any(word in content_lower for word in ['book', 'reserve', 'reservation']):
            return "Re: Reservation Request"
        elif any(word in content_lower for word in ['menu', 'food', 'drink', 'wine']):
            return "Re: Menu Inquiry"
        elif any(word in content_lower for word in ['hour', 'time', 'open']):
            return "Re: Operating Hours"
        elif any(word in content_lower for word in ['location', 'address', 'direction']):
            return "Re: Location Information"
        return "Re: Zevenwacht Restaurant Inquiry"

    def handle_incoming_email(self, email_content, from_email):
        try:
            logger.info(f"Processing incoming email from {from_email}")
            
            # Use ChatAgent to handle the message and maintain conversation history
            response = self.chat_agent.handle_message(
                message=email_content,
                channel='email',
                user_id=from_email
            )
            
            # Only prepare attachments if the response mentions menus
            attachments = []
            if 'menu' in response.lower() or 'à la carte' in response.lower() or 'wine list' in response.lower():
                content_lower = email_content.lower()
                attachments = self._prepare_attachments(content_lower)
                logger.info(f"Attaching menus based on AI response mentioning menus")
            
            # Format the response with attachment note and personalization
            formatted_response = self.format_email_response(
                response_text=response,
                has_attachments=bool(attachments),
                from_email=from_email
            )
            subject = self._determine_subject(email_content)
            
            # Send the response back via email with attachments
            success = self.send_email(
                to_email=from_email,
                subject=subject,
                message=formatted_response,
                attachments=attachments
            )

            if success:
                logger.info(f"Successfully processed and responded to email from {from_email}")
                return True
            else:
                logger.error(f"Failed to send response email to {from_email}")
                return False

        except Exception as e:
            logger.error(f"Error handling incoming email: {str(e)}")
            return False

    def _convert_html_to_pdf(self, html_file, pdf_file):
        """Convert HTML file to PDF"""
        try:
            # Configure pdfkit with wkhtmltopdf path
            config = pdfkit.configuration(wkhtmltopdf=r'wkhtmltopdf.exe')
            options = {
                'quiet': '',
                'enable-local-file-access': None
            }
            
            # Convert HTML to PDF
            pdfkit.from_file(html_file, pdf_file, options=options, configuration=config)
            return True
        except Exception as e:
            logger.error(f"Error converting HTML to PDF: {str(e)}")
            return False

    def _attach_file(self, msg, file_path, filename):
        """Attach a file to the email message"""
        try:
            with open(file_path, 'rb') as f:
                part = MIMEApplication(f.read(), Name=filename)
                part['Content-Disposition'] = f'attachment; filename="{filename}"'
                msg.attach(part)
            return True
        except Exception as e:
            logger.error(f"Error attaching file: {str(e)}")
            return False

    def _prepare_attachments(self, content_lower):
        """Prepare relevant attachments based on email content"""
        attachments = []
        added_menus = set()  # Track which menus we've already added
        
        def prepare_menu(base_name):
            if base_name in added_menus:
                return
            
            pdf_path = os.path.join(self.attachments_dir, f'{base_name}.pdf')
            
            # Only use existing PDFs
            if os.path.exists(pdf_path):
                logger.info(f"Adding existing PDF for {base_name}")
                attachments.append((f'{base_name}.pdf', pdf_path))
                added_menus.add(base_name)

        # If it's a menu inquiry, send available menus
        if 'menu' in content_lower:
            prepare_menu('a_la_carte_menu')
            prepare_menu('wine_list')
            prepare_menu('drinks_menu')

        return attachments

    def format_email_response(self, response_text, has_attachments=False, from_email=None):
        """Format the AI response into a professional email format"""
        # Get first name from email
        name = "Schalk"
        if from_email:
            # Extract name from email address if possible
            username = from_email.split('@')[0]
            # If username contains numbers or special characters, don't use it
            if username.isalpha():
                name_parts = username.split('.')
                if len(name_parts) > 0:
                    # Use the first part of the name if it's split by dots
                    name = name_parts[0].capitalize()
        
        # Format the response
        formatted_response = f"""Dear {name},

{response_text}

Warm regards,
Joline

--
Joline | Restaurant Sales Assistant
Zevenwacht Restaurant
Zevenwacht Wine Estate, Stellenbosch

Operating Hours:
Tuesday to Sunday: Breakfast 07:30-11:00, Main Service 12:00-22:00
Monday: Closed

Email: jolinesalesagent@gmail.com"""
        return formatted_response