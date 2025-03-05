from flask import Flask, request, render_template, jsonify, redirect, url_for
from handlers.call_handler import CallHandler
from handlers.whatsapp_handler import WhatsAppHandler
from handlers.sms_handler import SMSHandler
from handlers.email_handler import EmailHandler
from services.train_chat import TrainingChat

app = Flask(__name__)
call_handler = CallHandler()
whatsapp_handler = WhatsAppHandler()
sms_handler = SMSHandler()
email_handler = EmailHandler()
training_chat = TrainingChat()

@app.route('/webhook/voice', methods=['POST'])
def handle_call():
    if request.values.get('RecordingUrl'):
        recording_url = request.values.get('RecordingUrl')
        return call_handler.handle_recording(recording_url)
    return call_handler.handle_incoming_call()

@app.route('/webhook/whatsapp', methods=['POST'])
def handle_whatsapp():
    message_body = request.values.get('Body', '')
    from_number = request.values.get('From', '').replace('whatsapp:', '')
    return whatsapp_handler.handle_incoming_message(message_body, from_number)

@app.route('/webhook/sms', methods=['POST'])
def handle_sms():
    message_body = request.values.get('Body', '')
    from_number = request.values.get('From', '')
    return sms_handler.handle_incoming_message(message_body, from_number)

@app.route('/webhook/email', methods=['GET', 'POST'])
def handle_email():
    if request.method == 'GET':
        # Handle Gmail's verification request
        return "Email webhook verification successful", 200

    try:
        # Log raw request for debugging
        app.logger.info("Received email webhook request")
        app.logger.info(f"Form data: {request.form}")
        app.logger.info(f"Headers: {request.headers}")

        # Extract email details from Gmail forwarding format
        email_content = request.form.get('text', '')
        if not email_content:
            email_content = request.form.get('body', '')  # Alternative field name
        
        from_email = request.form.get('from', '')
        if not from_email:
            # Try to extract from the sender field
            from_email = request.form.get('sender', '')
        
        subject = request.form.get('subject', 'No Subject')

        # Log parsed email details
        app.logger.info(f"Parsed email - From: {from_email}, Subject: {subject}")
        
        # Handle the email
        success = email_handler.handle_incoming_email(
            email_content=email_content,
            from_email=from_email
        )
        
        if success:
            return {"status": "success", "message": "Email processed successfully"}, 200
        else:
            return {"status": "error", "message": "Failed to process email"}, 500
            
    except Exception as e:
        app.logger.error(f"Error processing email: {str(e)}")
        return {"status": "error", "message": str(e)}, 500

@app.route('/', methods=['GET'])
def index():
    """Redirect to the training interface"""
    return redirect(url_for('training_interface'))

@app.route('/training', methods=['GET', 'POST'])
def training_interface():
    """
    Web interface for training Joline.
    GET: Returns the training interface page
    POST: Processes a training message and returns the response
    """
    if request.method == 'GET':
        # Return a simple HTML interface for training
        return render_template('training.html')
    
    # Handle POST request (AJAX call from the training interface)
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if message.lower() == 'export':
            result = training_chat.export_restaurant_data()
            return jsonify({
                "response": result,
                "requires_confirmation": False
            })
        
        response = training_chat.process_training_message(message)
        
        # Check if the response requires confirmation
        requires_confirmation = False
        if training_chat.has_pending_confirmation():
            requires_confirmation = True
        
        return jsonify({
            "response": response,
            "requires_confirmation": requires_confirmation
        })
    
    except Exception as e:
        app.logger.error(f"Error processing training message: {str(e)}")
        return jsonify({
            "response": f"Error: {str(e)}",
            "requires_confirmation": False
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)