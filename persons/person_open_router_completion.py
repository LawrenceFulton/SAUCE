"""
This file contains a Person implementation which utilises the OpenRouter API with OpenAI models.
"""
from __future__ import annotations
import warnings
import os
import openai 
import time
from typing import List
from persons.person import Person
# Protect cyclic imports caused from typing
from typing import TYPE_CHECKING
#if TYPE_CHECKING:
from session_rooms.ChatEntry import ChatEntry

class PersonOpenRouterCompletion(Person):
    PERSON_TYPE = "person_open_router_completion"
    MODEL_NAME = "openai/gpt-4o-mini"
    MODEL_NAME = "openai/gpt-4.1-mini"
    # MODEL_NAME = "google/gemini-2.0-flash-001"
    # MODEL_NAME = "deepseek/deepseek-chat-v3-0324"
    # MODEL_NAME = "mistral/ministral-8b"
    # MODEL_NAME = "qwen/qwq-32b"
    # MODEL_NAME = "deepseek/deepseek-r1-distill-llama-70b"
    
    def __init__(self, background_story: str, name: str, *args, **kwargs):
        super().__init__(background_story, name)
        # Set up OpenAI client for OpenRouter with v0.27.7 structure
        self.model_name = PersonOpenRouterCompletion.MODEL_NAME
        openai.api_base = "https://openrouter.ai/api/v1"
        openai.api_key = os.getenv("OPENROUTER_API_KEY")
    
    def generate_answer(self, experiment_scenario: str, chat_list: List[ChatEntry]):
        generated_prompt: str = self.create_prompt(experiment_scenario, chat_list)

        print(f"Generated prompt: {generated_prompt}")  

        full_response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=[{"role": "user", "content": generated_prompt}],
            max_tokens=100,  # Limit the response length to 100 tokens.
            n=1,  # Generate a single response.
            temperature=0.6,  # Control the randomness of the output.
        )
        # Retrieve the generated response
        try:
            chat_answer: str = full_response.choices[0].message.content
        except Exception as e:
            warnings.warn(f"Error in OpenRouter API call: {e}")
            chat_answer = "Error: Unable to generate response."
        
        if not chat_answer:
            warnings.warn(f"Empty response from OpenRouter API.")
            print(full_response)
            chat_answer = "Error: Empty response."
        

        # if the response ends with a newline, remove it
        # needed for google/gemini-2.0-flash-001
        if chat_answer.endswith("\n"):
            chat_answer = chat_answer[:-1]

        # remove all "Me:" from the answer
        # needed for google/gemini-2.0-flash-001
        chat_answer = chat_answer.replace("Ich:", "")
        chat_answer = chat_answer.strip()
        # print(f"Chat answer: {chat_answer}")
        # print("##############################################")

        return ChatEntry(entity=self, prompt=generated_prompt, answer=chat_answer)
    
    def create_prompt(self, experiment_scenario: str, chat_list: List[ChatEntry]) -> str:
        """
        Creates a prompt with the past conversation formatted as a string.
        """
        output = ("Anweisungen:\n"
                f"Dein Name ist {self.name}.\n"
                f"Das Szenario ist folgendes: {experiment_scenario}\n"
                f"Das ist deine Hintergrundgeschichte: {self.background_story}\n\n"
                "Im Folgenden siehst du ein Gespräch zwischen dir und anderen Personen. "
                "Vervollständige deine nächste Antwort (beginnend mit 'Ich:'). "
                "Versuche, dich auf weniger als 30 Wörter zu beschränken. "
                "Antworte auf Deutsch.\n\n")

        
        for chat_entry in chat_list:
            cur_person = chat_entry.entity
            current_name = "Ich" if cur_person is self else cur_person.name
            output += f"{current_name}: {chat_entry.answer}\n"
        
        output += f"###################################\n"
        output += "Ich: "
        return output