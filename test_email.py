from handlers.email_handler import EmailHandler
import time

def test_email_conversation():
    # Initialize the email handler
    email_handler = EmailHandler()
    test_email = "test@example.com"  # Simulated sender email

    print("Email AI Agent Test Interface")
    print("Type 'exit' to end the conversation")
    print("-" * 50)

    # Test different types of email interactions
    test_scenarios = [
        {
            "subject": "Menu Inquiry",
            "content": "Hi, I'd like to know about your menu options.",
            "description": "Testing menu query"
        },
        {
            "subject": "Booking Request",
            "content": "I'd like to make a reservation for 4 people this Saturday at 7 PM.",
            "description": "Testing booking request"
        },
        {
            "subject": "Wine List",
            "content": "Could you please send me your wine list?",
            "description": "Testing wine list query"
        }
    ]

    for scenario in test_scenarios:
        print(f"\nTesting: {scenario['description']}")
        print(f"Subject: {scenario['subject']}")
        print(f"Content: {scenario['content']}")
        print("-" * 30)

        try:
            # Get AI response first
            response = email_handler.chat_agent.handle_message(
                message=scenario['content'],
                channel='email',
                user_id=test_email
            )
            
            print("\nJoline's Response:")
            print("-" * 50)
            print(response)
            print("-" * 50)

            # Now handle the email sending
            # First, get the AI response
            ai_response = email_handler.chat_agent.handle_message(
                message=scenario['content'],
                channel='email',
                user_id=test_email
            )
            
            # Format the response with the greeting
            formatted_response = email_handler.format_email_response(
                response_text=ai_response,
                has_attachments=False,
                from_email=test_email
            )
            
            print("\nFormatted Email Response:")
            print("-" * 50)
            print(formatted_response)
            print("-" * 50)
            
            # Now handle the full email sending
            success = email_handler.handle_incoming_email(
                email_content=scenario['content'],
                from_email=test_email
            )

            if success:
                print("\nEmail sent successfully!")
            else:
                print("\nFailed to send email.")

            # Add a small delay between tests
            time.sleep(1)

        except Exception as e:
            print(f"Error: {str(e)}")

    # Interactive testing
    print("\nEntering interactive mode. Type 'exit' to end.")
    print("-" * 50)

    while True:
        # Get user input
        subject = input("\nEnter email subject (or 'exit' to quit): ").strip()
        if subject.lower() == 'exit':
            break

        content = input("Enter email content: ").strip()
        
        try:
            # Get AI response first
            response = email_handler.chat_agent.handle_message(
                message=content,
                channel='email',
                user_id=test_email
            )
            
            print("\nJoline's Response:")
            print("-" * 50)
            print(response)
            print("-" * 50)

            # Format the response with the greeting
            formatted_response = email_handler.format_email_response(
                response_text=response,
                has_attachments=False,
                from_email=test_email
            )
            
            print("\nFormatted Email Response:")
            print("-" * 50)
            print(formatted_response)
            print("-" * 50)
            
            # Now handle the email sending
            success = email_handler.handle_incoming_email(
                email_content=content,
                from_email=test_email
            )

            if success:
                print("\nEmail sent successfully!")
            else:
                print("\nFailed to send email.")

        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    test_email_conversation()