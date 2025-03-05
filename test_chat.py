from services.chat_agent import ChatAgent

def main():
    # Initialize the chat agent
    agent = ChatAgent()
    print("AI Sales Agent Chat Interface")
    print("Type 'exit' to end the conversation or 'clear' to clear history")
    print("-" * 50)
    
    # Simulate a user session
    user_id = "console_user"
    channel = "test_console"
    
    # Display initial greeting
    print(f"\nJoline: {agent.greeting_message}")
    
    while True:
        # Get user input
        user_message = input("\nYou: ").strip()
        
        # Check for exit command
        if user_message.lower() == 'exit':
            break
        
        # Check for clear history command
        if user_message.lower() == 'clear':
            agent.clear_conversation_history(channel, user_id)
            print("Conversation history cleared!")
            continue
        
        # Get response from the agent
        response = agent.handle_message(user_message, channel, user_id)
        
        # Display the response
        print(f"\nJoline: {response}")
        
        # Optional: Display conversation history
        if user_message.lower() == 'history':
            history = agent.get_conversation_history(channel, user_id)
            print("\nConversation History:")
            for msg in history:
                role = "Joline" if msg['role'] == 'assistant' else "You"
                print(f"{role}: {msg['content']}")
            print("-" * 50)

if __name__ == "__main__":
    main()