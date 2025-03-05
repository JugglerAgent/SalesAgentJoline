# Fix PythonAnywhere Deployment Issues

You're currently experiencing an "Unhandled Exception" error with your PythonAnywhere deployment. Let's troubleshoot this step by step.

## Step 1: Check the Error Logs

First, let's check the error logs to understand what's causing the issue:

1. Log in to your PythonAnywhere account at https://www.pythonanywhere.com/login/
   - Username: JuggleAgent
   - Password: (use your password)

2. Go to the Web tab

3. Scroll down to the "Logs" section and click on the error log link:
   - `juggleagent.pythonanywhere.com.error.log`

4. Look for the most recent error messages, which will help identify the specific issue

## Step 2: Fix the WSGI Configuration File

The most common issue is an incorrect WSGI configuration:

1. In the Web tab, click on the WSGI configuration file link:
   - `/var/www/juggleagent_pythonanywhere_com_wsgi.py`

2. Replace the entire contents of the file with the following code:

```python
import sys
import os

# Add your project directory to the sys.path
path = '/home/JuggleAgent/SalesAgentJoline'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['FLASK_APP'] = 'main.py'

# Import your Flask app
try:
    from main import app as application
except ImportError as e:
    # Log the import error for debugging
    with open(os.path.join(os.path.dirname(__file__), 'import_error.log'), 'w') as f:
        f.write(f"Import Error: {str(e)}\n")
        f.write(f"sys.path: {sys.path}\n")
        f.write(f"Current directory: {os.getcwd()}\n")
        f.write(f"Files in {path}: {os.listdir(path) if os.path.exists(path) else 'Path does not exist'}\n")
    raise
```

3. Save the file

## Step 3: Verify the Project Structure

Make sure your project is properly cloned and structured:

1. Go to the Consoles tab
2. Start a new Bash console
3. Run the following commands to check your project structure:

```bash
cd
ls -la
# Check if SalesAgentJoline directory exists
ls -la SalesAgentJoline
# Check if main.py exists in the SalesAgentJoline directory
ls -la SalesAgentJoline/main.py
```

4. If the directory or file doesn't exist, clone the repository again:

```bash
cd
rm -rf SalesAgentJoline  # Remove the directory if it exists but is incomplete
git clone https://github.com/JugglerAgent/SalesAgentJoline.git
```

## Step 4: Install Required Packages

Make sure all required packages are installed:

1. In the same Bash console, run:

```bash
cd SalesAgentJoline
pip3 install --user -r requirements.txt
pip3 install --user flask python-dotenv
```

## Step 5: Create the Templates Directory

Ensure the templates directory exists:

1. In the same Bash console, run:

```bash
cd SalesAgentJoline
mkdir -p templates
```

2. Check if the training.html file exists:

```bash
ls -la templates/training.html
```

3. If it doesn't exist, create it:

```bash
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

## Step 6: Create a Simple Test Flask App

To verify that the basic Flask setup is working, let's create a simple test app:

1. In the Bash console, run:

```bash
cd
cd SalesAgentJoline
cat > test_flask_app.py << 'EOL'
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Flask! The basic setup is working."

if __name__ == '__main__':
    app.run(debug=True)
EOL
```

2. Update the WSGI file to use this test app:

```bash
cat > /var/www/juggleagent_pythonanywhere_com_wsgi.py << 'EOL'
import sys
import os

# Add your project directory to the sys.path
path = '/home/JuggleAgent/SalesAgentJoline'
if path not in sys.path:
    sys.path.append(path)

# Import the test Flask app
from test_flask_app import app as application
EOL
```

3. Reload the web app from the Web tab

4. Visit your site: https://juggleagent.pythonanywhere.com/

If this works, then the basic Flask setup is functioning, and the issue is with your main.py file.

## Step 7: Debugging the Main Flask App

If the test app works but the main app doesn't, let's debug the main.py file:

1. Create a simplified version of your main.py:

```bash
cd
cd SalesAgentJoline
cp main.py main_original.py  # Backup the original file
cat > main.py << 'EOL'
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello from the main Flask app! The basic setup is working."

@app.route('/training', methods=['GET', 'POST'])
def training_interface():
    if request.method == 'GET':
        try:
            return render_template('training.html')
        except Exception as e:
            return f"Error rendering template: {str(e)}", 500
    
    # Handle POST request (AJAX call from the training interface)
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        # Simple response for testing
        return jsonify({
            "response": f"You said: {message}",
            "requires_confirmation": False
        })
    
    except Exception as e:
        return jsonify({
            "response": f"Error: {str(e)}",
            "requires_confirmation": False
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
EOL
```

2. Update the WSGI file to use the main app again:

```bash
cat > /var/www/juggleagent_pythonanywhere_com_wsgi.py << 'EOL'
import sys
import os

# Add your project directory to the sys.path
path = '/home/JuggleAgent/SalesAgentJoline'
if path not in sys.path:
    sys.path.append(path)

# Import the Flask app
from main import app as application
EOL
```

3. Reload the web app from the Web tab

4. Visit your site: https://juggleagent.pythonanywhere.com/

5. Try the training interface: https://juggleagent.pythonanywhere.com/training

## Step 8: Gradually Restore Functionality

If the simplified version works, you can gradually restore the original functionality:

1. Compare the simplified main.py with the original main_original.py
2. Add back the original functionality piece by piece, testing after each addition
3. This will help identify which specific part of the code is causing the issue

## Additional Troubleshooting Tips

1. Check for missing dependencies:
   - Look for import errors in the error log
   - Install any missing packages with `pip3 install --user package_name`

2. Check for file path issues:
   - Make sure all file paths in your code are correct
   - Use absolute paths when necessary

3. Check for environment variables:
   - If your app requires environment variables, make sure they're set in the WSGI file

4. Check for file permissions:
   - Make sure all files and directories have the correct permissions

5. Check for syntax errors:
   - Make sure there are no syntax errors in your Python code

## Starting the Agent

Once the web app is properly configured and working, you can interact with the agent through:

1. The training interface at https://juggleagent.pythonanywhere.com/training
2. Email integration (if configured)
3. SMS/WhatsApp integration (if configured with Twilio)

The agent is already running as a web service on PythonAnywhere, so you don't need to manually start it. It will process requests as they come in through the various channels.