import requests
import os
from dotenv import load_dotenv
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get the API key
api_key = os.getenv("X_AI_API_KEY")  # Using the environment variable name from the prompt

def test_api_key():
    # Check if the API key is loaded
    if not api_key:
        logger.error("API key not found. Please set X_AI_API_KEY in your .env file.")
        return False

    # Log the key length and prefix for debugging (avoid logging the full key in production)
    logger.info(f"API key length: {len(api_key)}, starts with: {api_key[:2]}")

    # API endpoint
    url = "https://api.x.ai/v1/chat/completions"

    # Headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Minimal payload for testing
    payload = {
        "model": "claude-2",
        "messages": [{"role": "user", "content": "Hello, can you respond with 'Test successful'?"}],
        "temperature": 0.1,
        "max_tokens": 50
    }

    try:
        # Log the request details (masking the API key for security)
        logger.info(f"Sending request to {url}")
        masked_headers = headers.copy()
        masked_headers['Authorization'] = 'Bearer [MASKED]'
        logger.info(f"Headers: {masked_headers}")
        logger.info(f"Payload: {payload}")

        # Make the API call
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raises an exception for 4xx/5xx errors

        # Log and print the response
        response_data = response.json()
        logger.info(f"Response: {response_data}")
        print("API Key Test Successful!")
        print(f"Response from API: {response_data['choices'][0]['message']['content']}")
        return True

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    result = test_api_key()
    if result:
        logger.info("API key is valid and working.")
    else:
        logger.error("API key test failed.")