# PythonAnywhere Setup Instructions

These instructions will guide you through setting up your project on PythonAnywhere from scratch.

## Step 1: Clone the GitHub Repository to PythonAnywhere

1. Log in to your PythonAnywhere account at https://www.pythonanywhere.com/login/
   - Username: JuggleAgent
   - Password: (use your password)

2. Go to the "Consoles" tab

3. Start a new Bash console

4. In the Bash console, run the following commands to clone your GitHub repository:

```bash
# Go to your home directory
cd

# Remove any existing SalesAgentJoline directory (if it exists)
rm -rf SalesAgentJoline

# Clone the repository from GitHub
git clone https://github.com/JugglerAgent/SalesAgentJoline.git

# Verify that the files were cloned successfully
ls -la SalesAgentJoline
```

## Step 2: Set Up the Web App

1. Go to the "Web" tab

2. If you already have a web app, click on it. If not, click "Add a new web app"

3. Choose your domain name (it will be `juggleagent.pythonanywhere.com`)

4. Select "Manual configuration"

5. Choose Python 3.10 or newer

## Step 3: Configure the WSGI File

1. In the Web tab, click on the WSGI configuration file link (e.g., `/var/www/juggleagent_pythonanywhere_com_wsgi.py`)

2. Replace the entire contents of the file with the contents of the `simple_wsgi.py` file from your repository:

```bash
# In the Bash console, run:
cat ~/SalesAgentJoline/simple_wsgi.py > /var/www/juggleagent_pythonanywhere_com_wsgi.py
```

Or copy and paste the following code into the WSGI file editor:

```python
import sys
import os

# Add your project directory to the sys.path
path = '/home/JuggleAgent/SalesAgentJoline'
if path not in sys.path:
    sys.path.append(path)

# Import the test Flask app
try:
    from test_flask_app import app as application
    print("Successfully imported the test Flask app")
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
```

3. Save the file

## Step 4: Install Required Packages

1. In the Bash console, run:

```bash
cd ~/SalesAgentJoline
pip3 install --user -r requirements.txt
pip3 install --user flask python-dotenv
```

## Step 5: Reload the Web App

1. Go to the Web tab

2. Click the "Reload" button for your web app

3. Visit your site: https://juggleagent.pythonanywhere.com/

If you see "Hello from Flask! The basic setup is working.", then the basic Flask setup is working. If you see an error page with details about the import error, follow the troubleshooting steps in the `fix_pythonanywhere_wsgi.md` file.

## Step 6: Test the Training Interface

1. Visit: https://juggleagent.pythonanywhere.com/training

If this works, then the simplified training interface is working. You can now proceed to configure the WSGI file to use your main Flask app.

## Step 7: Configure the WSGI File to Use the Main Flask App

1. In the Web tab, click on the WSGI configuration file link

2. Replace the contents with:

```python
import sys
import os

# Add your project directory to the sys.path
path = '/home/JuggleAgent/SalesAgentJoline'
if path not in sys.path:
    sys.path.append(path)

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
    
    # Use the test Flask app as a fallback
    from test_flask_app import app as application
```

3. Save the file

4. Reload the web app

5. Visit your site: https://juggleagent.pythonanywhere.com/

If you encounter any issues, refer to the detailed troubleshooting guide in the `fix_pythonanywhere_wsgi.md` file.

## Additional Resources

- PythonAnywhere Help: https://help.pythonanywhere.com/
- Flask Documentation: https://flask.palletsprojects.com/
- GitHub Repository: https://github.com/JugglerAgent/SalesAgentJoline