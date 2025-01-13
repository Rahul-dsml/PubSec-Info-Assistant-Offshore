import json
import ast
from approaches.agent import (bot_response, 
                            #   prompt_creation, 
                              refine_question, 
                              main)

def prompt_creation(user_query, history=None):
    # if history:
    prompt = f"""You are an honest, persuasive, and dedicated Real-Estate agent AI assistant. Your task is to continue the ongoing conversation with the user regarding the property selection or recommendation or both.
    
    Conversation History: {history}
    User Query: {user_query}
    Based on this conversation history (if any) and current user query, you must follow below guidelines strictly:
    1. Always carefully analyze both the `Conversation History` and the `User Query`. As conversation history may contain the already recommended properties.
    2. Always review the Conversation History to determine if the user's property preferences (location, budget, property type, etc.) have already been collected. If Yes, avoid asking the user any follow up question for their preferences again.
    3. If any of these details for user's property preferences are missing, response in a friendly dialogue to collect the missed information.
    4. Use context from the Conversation History to avoid redundant information and offer smooth, follow-up answers.
    5. Always generate **very short**, crisp, precise, polite, generous and real estate professional response. Do not generate lengthy response.
    6. After collecting the user's property preferences, confirm the preferences with the user explicitly.
    
    YOU MUST GENERATE RESPONSE IN JSON FORMAT AS FOLLOWS:
    {{"SQL_QUERY": "BOOLEAN YES OR NO | Return 'YES' if the conversation history and current user query provide sufficient context to generate a valid SQL query; otherwise, return 'NO'.",
      "Response": "Your response to the conversation or initiating the conversation"}}

    THERE GENERATED RESPONSE MUST ALWAYS BE IN JSON AS DESCRIBED ABOVE WITH NO TAGS, EXPLANATION, ETC.
    
    """
    
    return prompt


# File paths (replace with your paths if needed)
csv_file_path = r"D:\Self\PubSec-Info-Assistant-Offshore\data\translated_file.csv"
sqlite_db_path = r"D:\Self\PubSec-Info-Assistant-Offshore\data\real_estate.db"

def assistant_chat():
    chat_history = []
    chat_language = "english"  # Default language for simplicity

    while True:
        # Simulate user input
        user_query = input("You: ")
        if user_query.lower() == "exit":
            print("Conversation terminated.")
            break

        # Generate response
        prompt = prompt_creation(user_query, chat_history)
        response = bot_response(prompt, language=chat_language)
        
        response = ast.literal_eval(response)
        print(response)
        print(f"Bot: {response['Response']}")

        if response['SQL_QUERY'].lower()== "yes":
            print("Processing terminate flow logic...")
            # response = response['Response'].lower().replace("terminate flow", "").strip().capitalize()
            refined_user_query = refine_question(chat_history, user_query)
            print(f"Refined Query: {refined_user_query}")
            generated_response = main(refined_user_query, csv_file_path, sqlite_db_path, chat_language)
            print(f"Insights: {generated_response}")

        # Update chat history
        chat_history.append({"user": user_query, "bot": response['Response']})

if __name__ == "__main__":
    assistant_chat()
