from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()
client = Groq(
    api_key= os.getenv("GROQ_API_KEY"),
)

def bot_response(prompt, language='English'):
    
    chat_completion = client.chat.completions.create(
        messages=[{'role': 'system', 'content': f'You are a real estate agent who talk in {language} language and helps customer in finding and buying properties in a very professional and polite way.'},
                {"role": "user", "content": prompt}],
        model="llama-3.2-90b-vision-preview",
        temperature=0,
        max_tokens=1024,
    )
    return chat_completion.choices[0].message.content.strip()

def prompt_creation(user_query, history):
    prompt = f"""You are a highly knowledgeable and professional real estate agent chatbot. Your primary responsibility is to assist users with property-related inquiries by providing clear, relevant, and professional responses. Leverage prior interactions to maintain continuity and coherence throughout the conversation.

        ### Guidelines
        1. Carefully analyze both the **conversation history** and the **current user query**.
        2. Use context from the conversation history to avoid redundant information and offer smooth, follow-up answers.
        3. Before recommending any properties, ensure that essential user details are gathered by checking the following checklist in the conversation history:
            - User's **name** to address user in future responses. THIS MUST BE THE FIRST QUESTION FOR USER ALWAYS. If user is not comfortable in sharing his/her name then move on.
            - Specific **property preferences** like (Ask below these in single question):
                - Location
                - Price range
                - Type of property
        If any of these details are missing, initiate a friendly dialogue to collect the missed information.
        Once User respond with all his/her property preferences then in response mention only "TERMINATE FLOW".
        4. Do not immediately answer property-specific questions without establishing a foundation of user preferences for a more tailored response.
        5. Use collected details to enhance the relevance and personalization of answers.
        6. For questions unrelated to real estate, respond courteously and guide users back to relevant topics.
        7. Always generate **very short**, crisp, precise, polite, generous and real estate professional response. Do not generate lengthy response.

        Example:
        Question: "Good morning!"
        Output: "Good morning! How can I assist you with your property search today?"

        Question: "Hi"
        Output: "Hello! How can I help you get your desired properties?"

        Question: "Hi, I would like to see some of the properties."
        Output: "Certainly! Before we proceed, may I have your name?"

        Conversation History: {history}

        Question: "{user_query}"
        Output:
        """
    
    return prompt

def chat(user_query, history):

    res = bot_response(prompt_creation(user_query, history), language='Arabic')
    # history += "Agent: " + res + '\n'
    return res
    