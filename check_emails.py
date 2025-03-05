import imaplib
import email
import time
import re
from handlers.email_handler import EmailHandler
from config.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_latest_reply(email_text, sender_email):
    """
    Extract only the latest reply content from an email thread.
    This function attempts to identify and remove quoted content from previous emails.
    """
    # If the email is very short, it's likely just a new message
    if len(email_text) < 100:
        return email_text.strip()
    
    # First, try to extract content by looking for quoted lines (starting with >)
    lines = email_text.split('\n')
    non_quoted_lines = []
    found_quoted = False
    
    for line in lines:
        if line.strip().startswith('>'):
            found_quoted = True
            continue
        # Skip empty lines right after quoted content
        if found_quoted and not line.strip():
            continue
        found_quoted = False
        non_quoted_lines.append(line)
    
    # If we found quoted content and extracted something meaningful
    extracted_by_quotes = '\n'.join(non_quoted_lines).strip()
    if found_quoted and len(extracted_by_quotes) > 20:
        return extracted_by_quotes
    
    # Common patterns that indicate the start of a quoted message
    patterns = [
        # Standard email client quote patterns
        r'\nOn .*wrote:',
        r'\n-----Original Message-----',
        r'\n-+Forwarded message-+',
        r'\nFrom:.*\nSent:.*\nTo:.*\nSubject:',
        # Joline's signature pattern
        r'\nWarm regards,\nJoline\n',
        r'\n--\nJoline \| Restaurant Sales Assistant',
        # Gmail's quote marker
        r'\nOn .* at .*, .* <.*> wrote:',
        # Outlook style
        r'\n-+Original Message-+',
        # Apple Mail style
        r'\nOn .*, .* wrote:',
        # Generic date-based patterns
        r'\nOn \d{1,2}/\d{1,2}/\d{2,4}',
        r'\nOn \w+, \w+ \d{1,2}, \d{4} at \d{1,2}:\d{2} [AP]M',
        # Common delimiters
        r'\n-{3,}',  # Three or more hyphens
        r'\n_{3,}',  # Three or more underscores
        r'\n\*{3,}', # Three or more asterisks
        # Email client specific
        r'\nSent from my iPhone',
        r'\nSent from my Android',
    ]
    
    # Find the earliest occurrence of any quote pattern
    earliest_pos = len(email_text)
    matching_pattern = None
    
    for pattern in patterns:
        matches = list(re.finditer(pattern, email_text))
        if matches:
            pos = matches[0].start()
            if pos < earliest_pos:
                earliest_pos = pos
                matching_pattern = pattern
    
    # Extract only the content before the quoted text
    if earliest_pos < len(email_text):
        logger.debug(f"Found quote pattern: {matching_pattern} at position {earliest_pos}")
        new_content = email_text[:earliest_pos].strip()
        
        # If we have very little content, we might have been too aggressive
        if len(new_content) < 10:
            # Try another approach - look for the first paragraph
            paragraphs = re.split(r'\n\s*\n', email_text)
            if paragraphs and len(paragraphs[0]) > 10:
                return paragraphs[0].strip()
        
        return new_content
    
    # If no quote patterns were found, try to split by empty lines
    # and take the first paragraph (often the new content)
    paragraphs = re.split(r'\n\s*\n', email_text)
    if len(paragraphs) > 1 and len(paragraphs[0]) > 10:
        return paragraphs[0].strip()
    
    # If all else fails, return the original text
    return email_text.strip()

def check_emails():
    """Check for new emails using IMAP"""
    email_handler = EmailHandler()
    processed_ids = set()  # Keep track of processed message IDs
    
    while True:
        try:
            # Connect to Gmail IMAP
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(Config.EMAIL_ADDRESS, Config.EMAIL_PASSWORD)
            mail.select("inbox")
            
            # Search for unread emails
            _, messages = mail.search(None, "UNSEEN")
            
            message_nums = messages[0].split()
            logger.info(f"Found {len(message_nums)} unread messages")
            
            # Process each unread message
            for num in message_nums:
                try:
                    # Get message ID
                    _, msg_data = mail.fetch(num, "(BODY[HEADER.FIELDS (MESSAGE-ID)])")
                    message_id = email.message_from_bytes(msg_data[0][1]).get("Message-ID", "")
                    
                    # Skip if already processed
                    if message_id in processed_ids:
                        logger.info(f"Skipping already processed message: {message_id}")
                        continue
                        
                    processed_ids.add(message_id)
                    
                    # Get email content
                    _, msg = mail.fetch(num, "(RFC822)")
                    email_body = msg[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Get sender and subject
                    from_email = email.utils.parseaddr(email_message["From"])[1]
                    subject = email_message["Subject"]
                    
                    # Check for reply headers
                    references = email_message.get("References", "")
                    in_reply_to = email_message.get("In-Reply-To", "")
                    is_reply_by_headers = bool(references) or bool(in_reply_to)
                    
                    logger.info(f"Processing email - From: {from_email}, Subject: {subject}")
                    if is_reply_by_headers:
                        logger.info("Email headers indicate this is a reply")
                    
                    # Get email content
                    text = ""
                    if email_message.is_multipart():
                        for part in email_message.walk():
                            if part.get_content_type() == "text/plain":
                                text += part.get_payload(decode=True).decode() + "\n"
                            elif part.get_content_type() == "text/html":
                                # Keep HTML signatures
                                text += f"\n[HTML_CONTENT]{part.get_payload(decode=True).decode()}[/HTML_CONTENT]\n"
                    else:
                        text = email_message.get_payload(decode=True).decode()
                    
                    # Extract only the new content from reply emails
                    logger.info(f"Original email content length: {len(text)} characters")
                    extracted_text = extract_latest_reply(text, from_email)
                    logger.info(f"Extracted message content ({len(extracted_text)} chars): {extracted_text[:100]}...")
                    
                    # Check if this is likely a reply
                    is_reply = is_reply_by_headers or "Re:" in subject or len(text) > 500
                    if is_reply:
                        logger.info("Detected as a reply email - extracting latest content only")
                    
                    # Handle the email
                    if extracted_text:
                        email_handler.handle_incoming_email(extracted_text, from_email)
                    
                except Exception as e:
                    logger.error(f"Error processing email: {str(e)}")
            
            # Clean up old message IDs (keep last 100)
            if len(processed_ids) > 100:
                processed_ids = set(list(processed_ids)[-100:])
            
            mail.close()
            mail.logout()
            
        except Exception as e:
            logger.error(f"Error checking emails: {str(e)}")
        
        # Wait before checking again
        time.sleep(10)

if __name__ == "__main__":
    logger.info("Starting email checker...")
    check_emails()