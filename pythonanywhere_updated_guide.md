# Updated PythonAnywhere Deployment Guide

This guide addresses the specific issue with setting up environment variables and using a virtualenv on PythonAnywhere.

## Setting Up a Virtualenv

Since you see a "Virtualenv" section instead of "Environment variables" in the Web tab, you can use a virtualenv to isolate your Python environment and manage dependencies.

1. **Create a virtualenv**:
   
   In a Bash console, run:

   ```bash
   cd
   python -m venv salesagent_venv
   ```

   This creates a virtualenv named `salesagent_venv` in your home directory.

2. **Activate the virtualenv and install dependencies**:

   ```bash
   source salesagent_venv/bin/activate
   cd SalesAgentJoline
   pip install -r requirements.txt
   pip install flask python-dotenv
   ```

3. **Configure the virtualenv in the Web tab**:
   
   - Go to the Web tab
   - In the "Virtualenv" section, enter the path to your virtualenv:
     ```
     /home/JuggleAgent/salesagent_venv
     ```
   - Click the "Save" button

## Setting Environment Variables in the WSGI File

Since you don't see the "Environment variables" section, you can set environment variables directly in the WSGI file:

1. **Create a .env file in your project directory**:

   ```bash
   cd
   cd SalesAgentJoline
   cat > .env << 'EOL'
   OPENAI_API_KEY=your_openai_api_key
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_PHONE_NUMBER=your_twilio_phone_number
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   EMAIL_ADDRESS=your_email_address
   EMAIL_PASSWORD=your_email_password
   XAI_API_KEY=your_xai_api_key
   EOL
   ```

   Replace the placeholder values with your actual API keys and credentials.

2. **Update the WSGI file to load environment variables**:

   ```bash
   cat > /var/www/juggleagent_pythonanywhere_com_wsgi.py << 'EOL'
   import sys
   import os
   
   # Add your project directory to the sys.path
   path = '/home/JuggleAgent/SalesAgentJoline'
   if path not in sys.path:
       sys.path.append(path)
   
   # Load environment variables from .env file
   try:
       from dotenv import load_dotenv
       dotenv_path = os.path.join(path, '.env')
       if os.path.exists(dotenv_path):
           load_dotenv(dotenv_path)
       else:
           print(f"Warning: .env file not found at {dotenv_path}")
   except ImportError:
       print("Warning: python-dotenv not installed, environment variables will not be loaded from .env file")
   
   # Set environment variables manually if needed
   # os.environ['OPENAI_API_KEY'] = 'your_openai_api_key'
   # os.environ['TWILIO_ACCOUNT_SID'] = 'your_twilio_account_sid'
   # os.environ['TWILIO_AUTH_TOKEN'] = 'your_twilio_auth_token'
   # os.environ['TWILIO_PHONE_NUMBER'] = 'your_twilio_phone_number'
   # os.environ['SMTP_SERVER'] = 'smtp.gmail.com'
   # os.environ['SMTP_PORT'] = '587'
   # os.environ['EMAIL_ADDRESS'] = 'your_email_address'
   # os.environ['EMAIL_PASSWORD'] = 'your_email_password'
   # os.environ['XAI_API_KEY'] = 'your_xai_api_key'
   
   # Import the Flask app
   try:
       from main import app as application
   except ImportError as e:
       # Log the import error for debugging
       error_log_path = os.path.join(os.path.dirname(__file__), 'import_error.log')
       with open(error_log_path, 'w') as f:
           f.write(f"Import Error: {str(e)}\n")
           f.write(f"sys.path: {sys.path}\n")
           f.write(f"Current directory: {os.getcwd()}\n")
           f.write(f"Files in {path}: {os.listdir(path) if os.path.exists(path) else 'Path does not exist'}\n")
       
       # Use the minimal Flask app as a fallback
       from flask import Flask
       application = Flask(__name__)
       
       @application.route('/')
       def error_page():
           with open(error_log_path, 'r') as f:
               error_details = f.read()
           
           return f"""
           <html>
           <head>
               <title>Import Error</title>
               <style>
                   body {{ font-family: Arial, sans-serif; padding: 20px; }}
                   pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }}
               </style>
           </head>
           <body>
               <h1>Import Error</h1>
               <p>There was an error importing the Flask application:</p>
               <pre>{error_details}</pre>
               <p>Please check your PythonAnywhere setup and make sure all files and directories exist.</p>
           </body>
           </html>
           """
   EOL
   ```

3. **Reload your web app**:
   
   - Go to the Web tab
   - Click the "Reload" button

## Testing with the Minimal Flask App

If you're still having issues, try using the minimal Flask app:

1. **Update the WSGI file to use the minimal Flask app**:

   ```bash
   cat > /var/www/juggleagent_pythonanywhere_com_wsgi.py << 'EOL'
   import sys
   import os
   
   # Add your project directory to the sys.path
   path = '/home/JuggleAgent/SalesAgentJoline'
   if path not in sys.path:
       sys.path.append(path)
   
   # Import the minimal Flask app
   try:
       from minimal_flask_app import app as application
       print("Successfully imported the minimal Flask app")
   except ImportError as e:
       # Log the import error for debugging
       error_log_path = os.path.join(os.path.dirname(__file__), 'import_error.log')
       with open(error_log_path, 'w') as f:
           f.write(f"Import Error: {str(e)}\n")
           f.write(f"sys.path: {sys.path}\n")
           f.write(f"Current directory: {os.getcwd()}\n")
           f.write(f"Files in {path}: {os.listdir(path) if os.path.exists(path) else 'Path does not exist'}\n")
       
       # Create a simple Flask app as a fallback
       from flask import Flask
       application = Flask(__name__)
       
       @application.route('/')
       def error_page():
           with open(error_log_path, 'r') as f:
               error_details = f.read()
           
           return f"""
           <html>
           <head>
               <title>Import Error</title>
               <style>
                   body {{ font-family: Arial, sans-serif; padding: 20px; }}
                   pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }}
               </style>
           </head>
           <body>
               <h1>Import Error</h1>
               <p>There was an error importing the Flask application:</p>
               <pre>{error_details}</pre>
               <p>Please check your PythonAnywhere setup and make sure all files and directories exist.</p>
           </body>
           </html>
           """
   EOL
   ```

2. **Reload your web app**:
   
   - Go to the Web tab
   - Click the "Reload" button

3. **Visit your site**:
   
   https://juggleagent.pythonanywhere.com/

## Checking Error Logs

If you're still having issues, check the error logs:

1. Go to the Web tab
2. Scroll down to the "Logs" section
3. Click on the error log link:
   - `juggleagent.pythonanywhere.com.error.log`
4. Check the server log as well:
   - `juggleagent.pythonanywhere.com.server.log`

These logs will provide more information about what's causing the error.

## Creating a Very Simple Test App

If all else fails, create a very simple test app directly on PythonAnywhere:

1. In a Bash console, run:

```bash
cd
mkdir -p test_flask
cd test_flask

cat > app.py << 'EOL'
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Flask! This is a test app."

if __name__ == '__main__':
    app.run(debug=True)
EOL
```

2. Update the WSGI file:

```bash
cat > /var/www/juggleagent_pythonanywhere_com_wsgi.py << 'EOL'
import sys
import os

# Add your project directory to the sys.path
path = '/home/JuggleAgent/test_flask'
if path not in sys.path:
    sys.path.append(path)

# Import the test Flask app
from app import app as application
EOL
```

3. Reload your web app and visit your site.

If this works, then the basic Flask setup is working, and the issue is with your main app.