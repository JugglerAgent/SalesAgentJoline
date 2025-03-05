# PythonAnywhere Deployment Guide

This guide will walk you through deploying your Restaurant Menu Management System to PythonAnywhere.

## Step 1: Create a New Web App

1. Log in to your PythonAnywhere account at https://www.pythonanywhere.com/login/
2. Go to the Web tab
3. Click on "Add a new web app"
4. Choose your domain name (it will be `jugglegent.pythonanywhere.com`)
5. Select "Manual configuration"
6. Choose Python 3.8 or newer

## Step 2: Clone Your GitHub Repository

1. Go to the "Consoles" tab
2. Start a new Bash console
3. Clone your GitHub repository:

```bash
cd
git clone https://github.com/JugglerAgent/SalesAgentJoline.git
```

## Step 3: Set Up a Virtual Environment

1. In the same Bash console, create a virtual environment:

```bash
cd SalesAgentJoline
python -m venv venv
source venv/bin/activate
```

## Step 4: Install Dependencies

1. First, update the requirements.txt file to include Flask:

```bash
echo "flask" >> requirements.txt
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Install wkhtmltopdf (system dependency):

```bash
# PythonAnywhere has wkhtmltopdf pre-installed, but if you need a specific version:
# Contact PythonAnywhere support to install it for you
```

## Step 5: Configure the WSGI File

1. Go back to the "Web" tab
2. Click on the WSGI configuration file link (e.g., `/var/www/jugglegent_pythonanywhere_com_wsgi.py`)
3. Replace the contents with the following (adjust paths as needed):

```python
import sys
import os
from dotenv import load_dotenv

# Add your project directory to the sys.path
path = '/home/JuggleAgent/SalesAgentJoline'
if path not in sys.path:
    sys.path.append(path)

# Load environment variables from .env file
dotenv_path = os.path.join(path, '.env')
load_dotenv(dotenv_path)

# Set environment variables
os.environ['FLASK_APP'] = 'main.py'

# Import your Flask app
from main import app as application
```

4. Save the file

## Step 6: Set Up Environment Variables

1. Go to the "Web" tab
2. Scroll down to the "Environment variables" section
3. Add the following environment variables from your .env file (use your actual values):

```
OPENAI_API_KEY=your_openai_api_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your_email_address
EMAIL_PASSWORD=your_email_password
XAI_API_KEY=your_xai_api_key
```

## Step 7: Configure Static Files and Templates

1. Go to the "Web" tab
2. Scroll down to the "Static files" section
3. Add an entry for `/static/` to point to `/home/JuggleAgent/SalesAgentJoline/static` (if you have static files)
4. Make sure your templates directory is accessible:

```bash
# In the Bash console
mkdir -p /home/JuggleAgent/SalesAgentJoline/templates
```

## Step 8: Reload Your Web App

1. Go to the "Web" tab
2. Click the "Reload" button for your web app

## Step 9: View Your Application

Your application should now be live at `http://jugglegent.pythonanywhere.com`

## Troubleshooting

If you encounter any issues:

1. Check the error logs in the "Web" tab
2. Ensure all dependencies are installed correctly:
   ```bash
   pip install flask twilio python-dotenv pdfkit
   ```
3. Verify that your WSGI file is configured properly
4. Make sure all required environment variables are set
5. Check if wkhtmltopdf is installed and accessible:
   ```bash
   which wkhtmltopdf
   ```
6. If you need to debug, you can add print statements to your WSGI file and check the error logs

## Important Notes

1. PythonAnywhere free accounts have limitations on outbound network access. If you're using a free account, you may need to whitelist external APIs like Twilio and OpenAI.
2. The webhooks for Twilio (SMS, WhatsApp, voice) will need to be updated to point to your PythonAnywhere URL.
3. For email handling, you may need to set up a different approach as Gmail forwarding might not work with PythonAnywhere.