import json
import re
import logging
from datetime import datetime, timedelta
from typing import Any, Sequence
from approaches.approach import Approach
from core.messagebuilder import MessageBuilder
from core.modelhelper import get_token_limit
from core.modelhelper import num_tokens_from_messages
from groq import Groq

class LlamaDirectApproach(Approach):

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

    system_message_chat_conversation = """You are a Groq LLama system. Your persona is {systemPersona} who helps users interact with a Large Language Model. {response_length_prompt}
        User persona is {userPersona}. You are having a conversation with a user and you need to provide a response.    

        {follow_up_questions_prompt}
        {injected_prompt}
        """
    follow_up_questions_prompt_content = """
        Generate three very brief follow-up questions that the user would likely ask next about their previous chat context. Use triple angle brackets to reference the questions, e.g. <<<Are there exclusions for prescriptions?>>>. Try not to repeat questions that have already been asked.
        Only generate questions and do not generate any text before or after the questions, such as 'Next Questions'
        """
    query_prompt_template = """Below is a history of the conversation so far, and a new question asked by the user that needs to be answered.
        Generate a search query based on the conversation and the new question. Treat each search term as an individual keyword. Do not combine terms in quotes or brackets.
        Do not include cited sources e.g info or doc in the search query terms.
        Do not include any text inside [] or <<<>>> in the search query terms.
        Do not include any special characters like '+'.
        If the question is not in {query_term_language}, translate the question to {query_term_language} before generating the search query.
        If you cannot generate a search query, return just the number 0.
        """

    
    response_prompt_few_shots = []
    def __init__(
        self,
        llama_client,
        query_term_language: str,
        model_name: str,
    ):
        self.query_term_language = query_term_language
        self.chatgpt_token_limit = get_token_limit(model_name)
        self.model_name = model_name
        self.client = llama_client

    def run(self, history: Sequence[dict[str, str]], overrides: dict[str, Any], thought_chain: dict[str, Any]) -> Any:
        user_persona = overrides.get("user_persona", "")
        system_persona = overrides.get("system_persona", "")
        response_length = int(overrides.get("response_length") or 1024)

        user_q = 'Generate response for: ' + history[-1]["user"]
        thought_chain["user_query"] = history[-1]["user"]

        follow_up_questions_prompt = (
            self.follow_up_questions_prompt_content
            if overrides.get("suggest_followup_questions")
            else ""
        )

        system_message = self.system_message_chat_conversation.format(
            injected_prompt="",
            follow_up_questions_prompt=follow_up_questions_prompt,
            response_length_prompt=self.get_response_length_prompt_text(
                response_length
            ),
            userPersona=user_persona,
            systemPersona=system_persona,
        )

        messages = self.get_messages_from_history(
            system_message,
            "gpt-4o",
            history,
            history[-1]["user"] + "\n\n",
            self.response_prompt_few_shots,
            max_tokens=self.chatgpt_token_limit - 500
        )

        try:
            chat_completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.6,
                max_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
            ) 

            msg_to_display = '\n\n'.join([str(message) for message in messages])

            full_response = ""  
            for chunk in chat_completion:
                if hasattr(chunk, "choices") and len(chunk.choices) > 0 and hasattr(chunk.choices[0], "delta"):
                    delta_content = chunk.choices[0].delta.content
                    if delta_content:
                        full_response += delta_content  # Aggregate content

            # Yield the final structured response
            yield json.dumps({
                "data_points": {},
                "thoughts": f"Searched for:<br>{user_q}<br><br>Conversations:<br>" + msg_to_display.replace('\n', '<br>'),
                "thought_chain": thought_chain,
                "response": full_response,
            }) + "\n"
                
        except Exception as e:
            logging.error(f"Error in LlamaDirectApproach: {e}")
            yield json.dumps({"error": f"An error occurred while generating the completion. {e}"}) + "\n"
            return
