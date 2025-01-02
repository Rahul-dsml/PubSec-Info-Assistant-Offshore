import json
import logging
from typing import Any, Sequence
import os
from langchain_groq import ChatGroq

from approaches.approach import Approach

class LLamaDirectApproach(Approach):

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

    system_message_chat_conversation = """You are a conversational assistant using the LLama model. Your persona is {systemPersona}, and your goal is to assist the user effectively. {response_length_prompt}
        User persona is {userPersona}. Provide concise, accurate, and helpful responses.

        {follow_up_questions_prompt}
        {injected_prompt}
    """

    follow_up_questions_prompt_content = """
        Generate three very brief follow-up questions that the user would likely ask next about their previous chat context. Use triple angle brackets to reference the questions, e.g. <<<Are there exclusions for prescriptions?>>>. Try not to repeat questions that have already been asked.
        Only generate questions and do not generate any text before or after the questions, such as 'Next Questions'.
    """

    def __init__(self, groq_model_name: str, groq_api_key: str):
        """
        Initialize the LLamaDirectApproach with Groq API settings.
        :param groq_model_name: The Groq model name.
        :param groq_api_key: API key for authentication.
        """
        self.groq_model_name = groq_model_name
        self.groq_api_key = groq_api_key

        # Initialize ChatGroq model
        self.llm = ChatGroq(
            model=self.groq_model_name,
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=self.groq_api_key
        )

    async def run(self, history: Sequence[dict[str, str]], overrides: dict[str, Any]) -> Any:
        """
        Run the conversational logic using LLama through Groq.
        :param history: A sequence of dictionaries representing the conversation history.
        :param overrides: Additional options to modify behavior.
        :return: The generated response.
        """
        user_persona = overrides.get("user_persona", "")
        system_persona = overrides.get("system_persona", "")
        response_length = int(overrides.get("response_length") or 1024)

        user_query = history[-1]["user"]

        follow_up_questions_prompt = (
            self.follow_up_questions_prompt_content
            if overrides.get("suggest_followup_questions")
            else ""
        )

        system_message = self.system_message_chat_conversation.format(
            injected_prompt="",
            follow_up_questions_prompt=follow_up_questions_prompt,
            response_length_prompt=f"Response should be less than {response_length} characters.",
            userPersona=user_persona,
            systemPersona=system_persona,
        )

        messages = self.get_messages_from_history(
            system_message,
            history,
            user_query + "\n\n",
            max_tokens=response_length
        )

        try:
            response = self.call_groq_api(messages)

            for chunk in response:
                yield json.dumps({"content": chunk}) + "\n"

        except Exception as e:
            logging.error(f"Error in LLamaDirectApproach: {e}")
            yield json.dumps({"error": f"An error occurred while generating the completion. {e}"}) + "\n"

    def call_groq_api(self, messages: list[dict]) -> list[str]:
        """
        Call the Groq API to generate a response using LLama.
        :param messages: A list of message dictionaries.
        :return: The generated response as a list of chunks.
        """
        # Format the messages for the Groq model
        formatted_messages = [
            ("system", messages[0]["content"]),
        ]
        for turn in messages[1:]:
            formatted_messages.append(("human", turn["content"]))

        # Invoke the Groq model
        ai_msg = self.llm.invoke(formatted_messages)

        # Split the response by newlines (as the original code expected chunks)
        return ai_msg.content.split("\n")

    def get_messages_from_history(self, system_message: str, history: Sequence[dict[str, str]], user_query: str, max_tokens: int) -> list[dict[str, str]]:
        """
        Construct the message payload for the Groq API based on history and the system message.
        :param system_message: The system prompt.
        :param history: The conversation history.
        :param user_query: The user query.
        :param max_tokens: Maximum tokens allowed for the response.
        :return: A list of message dictionaries.
        """
        messages = [
            {"role": self.SYSTEM, "content": system_message},
        ]

        for turn in history:
            messages.append({"role": self.USER, "content": turn["user"]})
            messages.append({"role": self.ASSISTANT, "content": turn.get("assistant", "")})

        messages.append({"role": self.USER, "content": user_query})
        return messages
