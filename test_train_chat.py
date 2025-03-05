import os
from services.train_chat import TrainingChat

def main():
    """
    Test the training chat functionality.
    This allows restaurant owners or managers to train Joline through conversation.
    """
    print("=== Joline Training Chat ===")
    print("Welcome to Joline's training interface.")
    print("You can update menu items, prices, specials, and restaurant information.")
    print("Type 'exit' to quit, 'export' to save changes to the knowledge base.")
    
    training_chat = TrainingChat()
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() == 'exit':
            print("Exiting training chat. Changes have been saved to restaurant_data.json.")
            break
        
        if user_input.lower() == 'export':
            result = training_chat.export_restaurant_data()
            print(f"Joline: {result}")
            continue
        
        response = training_chat.process_training_message(user_input)
        print(f"Joline: {response}")

if __name__ == "__main__":
    main()