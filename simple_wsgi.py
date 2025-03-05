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