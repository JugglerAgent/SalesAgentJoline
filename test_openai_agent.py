import os
from dotenv import load_dotenv
from services.openai_agent import OpenAIAgent

# Load environment variables from .env file
load_dotenv()

def main():
    """
    Simple console interface to test the OpenAI agent
    """
    print("AI Sales Agent Chat Interface")
    print("Type 'exit' to end the conversation or 'clear' to clear history")
    print("--------------------------------------------------")
    
    # Initialize the OpenAI agent
    agent = OpenAIAgent()
    
    # Initialize conversation history
    conversation_history = []
    
    # Add initial greeting
    greeting = "Good day, I'm Joline from Zevenwacht Restaurant. How may I assist you today?"
    print(f"\nJoline: {greeting}")
    conversation_history.append({
        'role': 'assistant',
        'content': greeting
    })
    
    # Main conversation loop
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        # Check for exit command
        if user_input.lower() == 'exit':
            break
        
        # Check for clear command
        if user_input.lower() == 'clear':
            conversation_history = []
            print("\nConversation history cleared.")
            continue
        
        # Add user message to history
        conversation_history.append({
            'role': 'user',
            'content': user_input
        })
        
        # Generate response
        response = agent.generate_response(
            message=user_input,
            conversation_history=conversation_history,
            channel='chat'
        )
        
        # Add agent response to history
        conversation_history.append({
            'role': 'assistant',
            'content': response
        })
        
        # Display response
        print(f"\nJoline: {response}")

if __name__ == "__main__":
    main()