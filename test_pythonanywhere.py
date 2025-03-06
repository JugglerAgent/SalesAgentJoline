"""
Test script for verifying the PythonAnywhere deployment.

This script checks:
1. If the required environment variables are set
2. If the required directories exist
3. If the required files exist
4. If the Flask app can be imported
5. If the OpenAI API key is valid
6. If the ElevenLabs API key is valid (if provided)

Usage:
    python test_pythonanywhere.py
"""

import os
import sys
import importlib.util
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_environment_variables():
    """Check if the required environment variables are set."""
    logger.info("Checking environment variables...")
    
    # Load environment variables from .env file
    load_dotenv()
    
    required_vars = [
        'OPENAI_API_KEY',
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN',
        'TWILIO_PHONE_NUMBER'
    ]
    
    optional_vars = [
        'ELEVENLABS_API_KEY',
        'ELEVENLABS_VOICE_ID',
        'SMTP_SERVER',
        'SMTP_PORT',
        'EMAIL_ADDRESS',
        'EMAIL_PASSWORD',
        'XAI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    logger.info("All required environment variables are set.")
    
    missing_optional_vars = []
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional_vars.append(var)
    
    if missing_optional_vars:
        logger.warning(f"Missing optional environment variables: {', '.join(missing_optional_vars)}")
    
    return True

def check_directories():
    """Check if the required directories exist."""
    logger.info("Checking directories...")
    
    required_dirs = [
        'attachments',
        'templates'
    ]
    
    missing_dirs = []
    for dir_name in required_dirs:
        if not os.path.isdir(dir_name):
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        logger.error(f"Missing required directories: {', '.join(missing_dirs)}")
        logger.info("Creating missing directories...")
        for dir_name in missing_dirs:
            os.makedirs(dir_name, exist_ok=True)
            logger.info(f"Created directory: {dir_name}")
    
    logger.info("All required directories exist.")
    return True

def check_files():
    """Check if the required files exist."""
    logger.info("Checking files...")
    
    required_files = [
        'main.py',
        'templates/training.html'
    ]
    
    missing_files = []
    for file_name in required_files:
        if not os.path.isfile(file_name):
            missing_files.append(file_name)
    
    if missing_files:
        logger.error(f"Missing required files: {', '.join(missing_files)}")
        return False
    
    logger.info("All required files exist.")
    return True

def check_flask_app():
    """Check if the Flask app can be imported."""
    logger.info("Checking Flask app...")
    
    try:
        spec = importlib.util.spec_from_file_location("main", "main.py")
        main = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main)
        
        if hasattr(main, 'app'):
            logger.info("Flask app imported successfully.")
            return True
        else:
            logger.error("main.py does not contain a Flask app.")
            return False
    except Exception as e:
        logger.error(f"Error importing Flask app: {str(e)}")
        return False

def check_openai_api():
    """Check if the OpenAI API key is valid."""
    logger.info("Checking OpenAI API key...")
    
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        logger.error("OpenAI API key not set.")
        return False
    
    try:
        import openai
        openai.api_key = openai_api_key
        
        # Make a simple API call to check if the key is valid
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, world!"}
            ],
            max_tokens=5
        )
        
        logger.info("OpenAI API key is valid.")
        return True
    except Exception as e:
        logger.error(f"Error checking OpenAI API key: {str(e)}")
        return False

def check_elevenlabs_api():
    """Check if the ElevenLabs API key is valid (if provided)."""
    logger.info("Checking ElevenLabs API key...")
    
    elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
    elevenlabs_voice_id = os.getenv('ELEVENLABS_VOICE_ID')
    
    if not elevenlabs_api_key or not elevenlabs_voice_id:
        logger.warning("ElevenLabs API key or voice ID not set. Skipping check.")
        return True
    
    try:
        import requests
        
        # Make a simple API call to check if the key is valid
        url = "https://api.elevenlabs.io/v1/user"
        headers = {
            "Accept": "application/json",
            "xi-api-key": elevenlabs_api_key
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            logger.info("ElevenLabs API key is valid.")
            
            # Check if the voice ID is valid
            url = f"https://api.elevenlabs.io/v1/voices/{elevenlabs_voice_id}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                logger.info("ElevenLabs voice ID is valid.")
                return True
            else:
                logger.error(f"Invalid ElevenLabs voice ID: {response.status_code} - {response.text}")
                return False
        else:
            logger.error(f"Invalid ElevenLabs API key: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error checking ElevenLabs API key: {str(e)}")
        return False

def main():
    """Run all checks."""
    logger.info("Starting PythonAnywhere deployment test...")
    
    checks = [
        check_environment_variables,
        check_directories,
        check_files,
        check_flask_app,
        check_openai_api,
        check_elevenlabs_api
    ]
    
    results = []
    for check in checks:
        results.append(check())
    
    if all(results):
        logger.info("All checks passed! The PythonAnywhere deployment is ready.")
        return 0
    else:
        logger.error("Some checks failed. Please fix the issues and try again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())