# Deploying Joline with Voice Capabilities to PythonAnywhere

This guide provides step-by-step instructions for deploying the Joline AI agent with voice capabilities to PythonAnywhere.

## Prerequisites

1. A PythonAnywhere account
2. Your GitHub repository with the Joline project
3. API keys for:
   - OpenAI
   - Twilio
   - ElevenLabs (for voice capabilities)

## Step 1: Clone the Repository

1. Log in to your PythonAnywhere account
2. Open a Bash console
3. Clone your GitHub repository:

```bash
cd
git clone https://github.com/JugglerAgent/SalesAgentJoline.git
```

## Step 2: Set Up a Python 3.8 Virtual Environment

PythonAnywhere supports Python 3.8, which is required for this project:

```bash
cd
python3.8 -m venv salesagent_venv_py38
source salesagent_venv_py38/bin/activate
cd SalesAgentJoline
pip install -r requirements.txt
```

## Step 3: Create Required Directories

Make sure the attachments directory exists for storing audio files:

```bash
cd ~/SalesAgentJoline
mkdir -p attachments
mkdir -p templates
```

## Step 4: Create the .env File

Create a .env file with all the required environment variables:

```bash
cd ~/SalesAgentJoline
cat > .env << 'EOL'
OPENAI_API_KEY=your_openai_api_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
TWILIO_SA_PHONE_NUMBER=your_twilio_sa_phone_number
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_elevenlabs_voice_id
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your_email_address
EMAIL_PASSWORD=your_email_password
XAI_API_KEY=your_xai_api_key
EOL
```

Replace the placeholder values with your actual API keys and credentials.

## Step 5: Create the training.html Template

Make sure the training.html template exists:

```bash
cd ~/SalesAgentJoline
cat > templates/training.html << 'EOL'
<!DOCTYPE html>
<html>
<head>
    <title>Joline Training Interface</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        #chat-container {
            border: 1px solid #ccc;
            padding: 10px;
            height: 400px;
            overflow-y: auto;
            margin-bottom: 10px;
        }
        .message {
            margin-bottom: 10px;
            padding: 8px;
            border-radius: 5px;
        }
        .user-message {
            background-color: #e6f7ff;
            text-align: right;
        }
        .bot-message {
            background-color: #f2f2f2;
        }
        #message-form {
            display: flex;
        }
        #message-input {
            flex-grow: 1;
            padding: 8px;
            margin-right: 10px;
        }
        button {
            padding: 8px 16px;
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <h1>Joline Training Interface</h1>
    <div id="chat-container"></div>
    <form id="message-form">
        <input type="text" id="message-input" placeholder="Type your message here..." required>
        <button type="submit">Send</button>
    </form>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const chatContainer = document.getElementById('chat-container');
            const messageForm = document.getElementById('message-form');
            const messageInput = document.getElementById('message-input');
            
            // Add a welcome message
            addBotMessage("Welcome to the Joline Training Interface. How can I help you today?");
            
            messageForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const message = messageInput.value.trim();
                if (message) {
                    // Add user message to chat
                    addUserMessage(message);
                    
                    // Send message to server
                    fetch('/training', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ message: message }),
                    })
                    .then(response => response.json())
                    .then(data => {
                        // Add bot response to chat
                        addBotMessage(data.response);
                        
                        // If confirmation is required, add a note
                        if (data.requires_confirmation) {
                            addBotMessage("Please confirm this action by typing 'yes' or 'no'.");
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        addBotMessage("Sorry, there was an error processing your request.");
                    });
                    
                    // Clear input field
                    messageInput.value = '';
                }
            });
            
            function addUserMessage(text) {
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message user-message';
                messageDiv.textContent = text;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
            
            function addBotMessage(text) {
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message bot-message';
                messageDiv.textContent = text;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        });
    </script>
</body>
</html>
EOL
```

## Step 6: Set Up the Web App

1. Go to the Web tab in PythonAnywhere
2. Click "Add a new web app"
3. Choose your domain name (e.g., yourusername.pythonanywhere.com)
4. Select "Manual configuration"
5. Choose Python 3.8
6. In the "Virtualenv" section, enter the path to your virtualenv:
   ```
   /home/yourusername/salesagent_venv_py38
   ```
7. Click "Save"

## Step 7: Configure the WSGI File

1. In the Web tab, click on the WSGI configuration file link
2. Replace the contents with:

```python
import sys
import os

# Add your project directory to the sys.path
path = '/home/yourusername/SalesAgentJoline'
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

# Import the Flask app
try:
    from main import app as application
    print("Successfully imported the Flask app from main.py")
except ImportError as e:
    # Log the import error for debugging
    error_log_path = os.path.join(os.path.dirname(__file__), 'import_error.log')
    with open(error_log_path, 'w') as f:
        f.write(f"Import Error: {str(e)}\n")
        f.write(f"sys.path: {sys.path}\n")
        f.write(f"Current directory: {os.getcwd()}\n")
        f.write(f"Files in {path}: {os.listdir(path) if os.path.exists(path) else 'Path does not exist'}\n")
    
    # Use a minimal Flask app as a fallback
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
```

Replace `yourusername` with your actual PythonAnywhere username.

## Step 8: Configure Static Files

1. In the Web tab, scroll down to the "Static files" section
2. Add a new static files mapping:
   - URL: /attachments
   - Directory: /home/yourusername/SalesAgentJoline/attachments
3. Click "Save"

This will allow the attachments directory to be accessible via the web app.

## Step 9: Update Twilio Webhooks

Since PythonAnywhere doesn't support ngrok, you'll need to update your Twilio webhooks to point to your PythonAnywhere URL:

1. Log in to your Twilio account
2. Go to the Phone Numbers section
3. Click on your South African phone number
4. In the "Voice & Fax" section, update the "A Call Comes In" webhook to:
   ```
   https://yourusername.pythonanywhere.com/webhook/voice
   ```
5. Save the changes

## Step 10: Reload the Web App

1. Go to the Web tab
2. Click the "Reload" button

## Step 11: Test the Deployment

1. Visit your PythonAnywhere URL:
   ```
   https://yourusername.pythonanywhere.com/
   ```
2. You should be redirected to the training interface
3. Try sending a message to test if the AI agent is working
4. Make a call to your Twilio South African phone number to test the voice capabilities

## Troubleshooting

### Common Issues

1. **Import Errors**:
   - Check the error logs in the Web tab
   - Make sure all required packages are installed in your virtualenv
   - Verify that the path to your project directory is correct in the WSGI file

2. **Environment Variables**:
   - Make sure your .env file exists and contains all the required variables
   - Check that the dotenv package is installed

3. **File Permissions**:
   - Make sure the attachments directory is writable by the web app
   - Check that the templates directory is readable by the web app

4. **Voice Capabilities**:
   - If voice capabilities aren't working, check that the ElevenLabs API key and voice ID are correctly set
   - Verify that the Twilio webhooks are correctly configured

### Checking Logs

To check the logs for your web app:

1. Go to the Web tab
2. Scroll down to the "Logs" section
3. Click on the error log link
4. Check for any error messages

## Limitations

1. **Voice Capabilities**:
   - PythonAnywhere's free tier has CPU and memory limitations that may affect voice generation performance
   - Consider upgrading to a paid plan for better performance

2. **File Storage**:
   - PythonAnywhere's free tier has limited file storage
   - Audio files generated by ElevenLabs may consume storage space quickly

3. **Outbound Calls**:
   - Making outbound calls from PythonAnywhere may not work as expected
   - Consider using a different service for outbound calls

## Conclusion

You've successfully deployed Joline with voice capabilities to PythonAnywhere. The web app is now accessible via your PythonAnywhere URL, and the voice capabilities are available through your Twilio South African phone number.