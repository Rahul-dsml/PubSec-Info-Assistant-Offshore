from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()
client = Groq(
    api_key= os.getenv("GROQ_API_KEY"),
)

def bot_response(prompt, language='English'):
    
    chat_completion = client.chat.completions.create(
        messages=[{'role': 'system', 'content': f'You are a Real Estate agent who talk in {language} language and helps customer in finding and buying properties in a very professional and polite way.'},
                {"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile", # "llama-3.2-90b-vision-preview",
        temperature=0,
        max_tokens=1024,
    )
    return chat_completion.choices[0].message.content.strip()

def prompt_creation(user_query, history):
    prompt = f"""You are an honest, persuasive, and dedicated Real-Estate agent AI assistant. Your first task is to identify the user defined criteria or preferences like location, budget, property type, etc. But you should not bore the user by so many follow up questions. 

    # Please follow below guidelines strictly:
    1. Always carefully analyze both the `conversation history` and the `current user query`.
    2. Use context from the conversation history to avoid redundant information and offer smooth, follow-up answers.
    3. Before recommending any properties, ensure that essential user details are gathered by checking the following checklist in the conversation history:
        - Always begin the conversation by asking the user for their name to address them in future responses. If the user is not comfortable sharing their name, proceed without insisting and move on to assist them with their query.
        - Always ask the user to provide their specific property preferences in a single question. Include the following details: location, price range, type of property (e.g. apartment, house, commercial), and any other important criteria they may have for the property search.
    4. Always review the Conversation History to determine if the user's property preferences have already been collected. If they have, respond with the exact phrase 'TERMINATE FLOW' and avoid asking the user for their preferences again.
    5. If any of these details are missing, initiate a friendly dialogue to collect the missed information.
    6. Do not immediately answer property-specific questions without establishing a foundation of user preferences for a more tailored response.
    7. Use collected details to enhance the relevance and personalization of answers.
    8. For questions unrelated to real estate, respond courteously and guide users back to relevant topics.
    9. Always generate **very short**, crisp, precise, polite, generous and real estate professional response. Do not generate lengthy response.
    10. After collecting the user's property preferences, confirm the preferences with the user explicitly. Once the user confirms, respond only with the exact phrase 'TERMINATE FLOW' and nothing else. Do not include any additional text, explanation, or response.

    Example:
    User: Good morning!
    Assistant: Good morning! How can I assist you with your property search today?
    User: Hi
    Assistant: Hello! How can I help you get your desired properties?
    User: Hi, I would like to see some of the properties.
    Assistant: Certainly! Before we proceed, may I have your name?

    Conversation History: {history}
    User: {user_query}
    Assistant:
    """
    
    return prompt


def refine_question(history,user_query):
    history.append({'role': 'user', 'content': user_query})
    prompt=f"""You are a Real Estate helpful assistant who helps user to recommend best properties based on user property preferences. Your task is to refine the final user query based on the conversation history given below: 
    1. Always write the final refine query in english language.
    2. Final refined query must contain all user define criteria of property preferences from conversation history given by user.
    3. The final output must be the final refined query. Do not add any extra text.
    """
    chat_completion = client.chat.completions.create(
        messages=[{'role': 'system', 'content': prompt},
                {"role": "user", "content": str(history)}],
        model="llama-3.2-90b-vision-preview",
        temperature=0,
        max_tokens=1024,
    )
    return chat_completion.choices[0].message.content.strip()



def chat(user_query, history):

    res = bot_response(prompt_creation(user_query, history), language='Arabic')
    response=res.replace('"',"")
    # if "terminate flow" in response.lower():

    return res
    