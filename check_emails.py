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
    logger.info(f"EXTRACTION DEBUG - Original email text: {email_text[:200]}...")
    
    # If the email is very short, it's likely just a new message
    if len(email_text) < 100:
        logger.info(f"EXTRACTION DEBUG - Email is short (<100 chars), returning as is")
        return email_text.strip()
    
    # First, try to extract content by looking for quoted lines (starting with >)
    lines = email_text.split('\n')
    logger.info(f"EXTRACTION DEBUG - Split into {len(lines)} lines")
    
    non_quoted_lines = []
    found_quoted = False
    
    for i, line in enumerate(lines):
        if line.strip().startswith('>'):
            found_quoted = True
            logger.info(f"EXTRACTION DEBUG - Found quoted line {i}: {line[:50]}...")
            continue
        # Skip empty lines right after quoted content
        if found_quoted and not line.strip():
            continue
        found_quoted = False
        non_quoted_lines.append(line)
    
    # If we found quoted content and extracted something meaningful
    extracted_by_quotes = '\n'.join(non_quoted_lines).strip()
    if found_quoted and len(extracted_by_quotes) > 20:
        logger.info(f"EXTRACTION DEBUG - Extracted by quotes: {extracted_by_quotes[:100]}...")
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
            logger.info(f"EXTRACTION DEBUG - Found pattern '{pattern}' at position {pos}")
            if pos < earliest_pos:
                earliest_pos = pos
                matching_pattern = pattern
    
    # Extract only the content before the quoted text
    if earliest_pos < len(email_text):
        logger.info(f"EXTRACTION DEBUG - Found quote pattern: {matching_pattern} at position {earliest_pos}")
        new_content = email_text[:earliest_pos].strip()
        
        # If we have very little content, we might have been too aggressive
        if len(new_content) < 10:
            logger.info(f"EXTRACTION DEBUG - Extracted content too short (<10 chars): '{new_content}'")
            # Try another approach - look for the first paragraph
            paragraphs = re.split(r'\n\s*\n', email_text)
            logger.info(f"EXTRACTION DEBUG - Split into {len(paragraphs)} paragraphs")
            if paragraphs and len(paragraphs[0]) > 10:
                logger.info(f"EXTRACTION DEBUG - Using first paragraph: {paragraphs[0][:100]}...")
                return paragraphs[0].strip()
        
        logger.info(f"EXTRACTION DEBUG - Final extracted content: {new_content[:100]}...")
        return new_content
    
    # If no quote patterns were found, check if we have multiple paragraphs
    paragraphs = re.split(r'\n\s*\n', email_text)
    logger.info(f"EXTRACTION DEBUG - No patterns found, split into {len(paragraphs)} paragraphs")
    
    # Check if we have HTML content in the email
    html_content_index = -1
    for i, para in enumerate(paragraphs):
        if '[HTML_CONTENT]' in para:
            html_content_index = i
            logger.info(f"EXTRACTION DEBUG - Found HTML content in paragraph {i}")
            break
    
    # If we found HTML content, only use paragraphs before it
    if html_content_index > 0:
        # Join all paragraphs before the HTML content
        content_before_html = '\n\n'.join(paragraphs[:html_content_index]).strip()
        logger.info(f"EXTRACTION DEBUG - Using content before HTML: {content_before_html[:100]}...")
        return content_before_html
    
    # If we have multiple paragraphs but no HTML marker, join all non-signature paragraphs
    # (Exclude common signature indicators like "Kind regards", "Thanks", etc.)
    if len(paragraphs) > 1:
        # Check for signature indicators
        signature_indicators = ['kind regards', 'regards', 'thanks', 'thank you', 'cheers', 'sincerely', 'best wishes']
        content_paragraphs = []
        
        for para in paragraphs:
            para_lower = para.lower().strip()
            # Skip if it's just a signature line
            if any(indicator in para_lower for indicator in signature_indicators) and len(para_lower) < 30:
                logger.info(f"EXTRACTION DEBUG - Skipping signature paragraph: {para}")
                continue
            content_paragraphs.append(para)
        
        # Join all content paragraphs
        full_content = '\n\n'.join(content_paragraphs).strip()
        logger.info(f"EXTRACTION DEBUG - Using full content: {full_content[:100]}...")
        return full_content
    
    # If all else fails, return the original text
    logger.info(f"EXTRACTION DEBUG - Returning original text")
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