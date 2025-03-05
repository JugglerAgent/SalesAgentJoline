from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Flask! The basic setup is working."

@app.route('/test')
def test():
    return "This is a test route. If you can see this, routing is working correctly."

@app.route('/training', methods=['GET', 'POST'])
def training_interface():
    if request.method == 'GET':
        try:
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Simple Training Interface</title>
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
                        height: 200px;
                        overflow-y: auto;
                        margin-bottom: 10px;
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
                </style>
            </head>
            <body>
                <h1>Simple Training Interface</h1>
                <p>This is a simplified version of the training interface to test if Flask is working correctly.</p>
                <div id="chat-container">
                    <div>Welcome to the simple training interface!</div>
                </div>
                <form id="message-form">
                    <input type="text" id="message-input" placeholder="Type your message here..." required>
                    <button type="submit">Send</button>
                </form>
                
                <script>
                    document.addEventListener('DOMContentLoaded', function() {
                        const chatContainer = document.getElementById('chat-container');
                        const messageForm = document.getElementById('message-form');
                        const messageInput = document.getElementById('message-input');
                        
                        messageForm.addEventListener('submit', function(e) {
                            e.preventDefault();
                            const message = messageInput.value.trim();
                            if (message) {
                                // Add user message to chat
                                const userDiv = document.createElement('div');
                                userDiv.textContent = 'You: ' + message;
                                chatContainer.appendChild(userDiv);
                                
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
                                    const botDiv = document.createElement('div');
                                    botDiv.textContent = 'Bot: ' + data.response;
                                    chatContainer.appendChild(botDiv);
                                })
                                .catch(error => {
                                    console.error('Error:', error);
                                    const errorDiv = document.createElement('div');
                                    errorDiv.textContent = 'Error: Could not send message';
                                    chatContainer.appendChild(errorDiv);
                                });
                                
                                // Clear input field
                                messageInput.value = '';
                            }
                        });
                    });
                </script>
            </body>
            </html>
            """
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