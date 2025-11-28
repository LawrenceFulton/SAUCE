"""
This file contains a Person implementation which utilises the OpenRouter API with OpenAI models.
"""

from __future__ import annotations
import os
from openai import OpenAI
from typing import List, Literal, cast
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam as SysMessage,
    ChatCompletionAssistantMessageParam as AssistantMessage,
    ChatCompletionUserMessageParam as UserMessage,
)
from persons.person import Person
from session_rooms.ChatEntry import ChatEntry
from session_rooms.session_room import System


class PersonOpenRouterCompletion(Person):
    PERSON_TYPE = "person_open_router_completion"
    MODEL_NAME = "openai/gpt-4o-mini"
    MODEL_NAME = "openai/gpt-4.1-mini"
    # MODEL_NAME = "openai/gpt-4.1"
    # MODEL_NAME = "google/gemini-2.5-flash-preview"
    # MODEL_NAME = "google/gemini-2.0-flash-001"
    # MODEL_NAME = "deepseek/deepseek-chat-v3-0324"
    # MODEL_NAME = "qwen/qwq-32b"
    # MODEL_NAME = "deepseek/deepseek-r1-distill-llama-70b"

    # MODEL_NAME = "mistralai/mixtral-8x7b-instruct"

    MODEL_NAME = "mistralai/mistral-7b-instruct"
    MODEL_NAME = "openai/gpt-3.5-turbo-instruct"


    def __init__(
        self,
        background_story: str,
        you_background_story: str,
        name: str,
        prompt_version: str = "v0",
        *args,
        **kwargs,
    ):
        super().__init__(background_story,you_background_story, name)

        self.model_name = PersonOpenRouterCompletion.MODEL_NAME
        self.client = OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )

    def generate_answer(
        self,
        experiment_scenario: str,
        chat_list: List[ChatEntry],
        prompt_version: str,
        is_questionnaire: bool = False,
    ):
        generated_prompt: List[ChatCompletionMessageParam] = self.create_prompt(
            experiment_scenario, chat_list, prompt_version, is_questionnaire
        )

        full_response = self.client.chat.completions.create(
            model=self.model_name,
            messages=generated_prompt,
            max_tokens=100,
            n=1,
            temperature=0.1,
        )
        # Retrieve the generated response (updated for new OpenAI package)
        output_text: str | None = full_response.choices[0].message.content
        parsed_answer = output_text if output_text else ""

        parsed_answer = (
            parsed_answer.removeprefix("Me: ").removeprefix(f"{self.name}: ").strip()
        )

        return ChatEntry(entity=self, prompt=generated_prompt, answer=parsed_answer)

    def create_prompt(
        self,
        experiment_scenario: str,
        chat_list: List[ChatEntry],
        prompt_version: str,
        is_questionnaire: bool = False,
    ) -> List[ChatCompletionMessageParam]:


        assert prompt_version in [
            "v0",
            "v1",
            "v2",
        ], f"Unknown prompt version {prompt_version}. Please use v0, v1 or v2."
        prompt_version_literal: Literal["v0", "v1", "v2"] = cast(
            Literal["v0", "v1", "v2"], prompt_version
        )
        conversation: List[ChatCompletionMessageParam] = super().prompt_setups(
            experiment_scenario=experiment_scenario,
            prompt_version=prompt_version_literal,
            is_questionnaire=is_questionnaire,
        )

        for chat_entry in chat_list:
            if isinstance(chat_entry.entity, System):  # System message
                conversation.append(UserMessage(role="user", content=chat_entry.answer))
            elif chat_entry.entity.name == self.name:  # This person's message
                conversation.append(
                    AssistantMessage(
                        role="assistant",
                        content=f"{chat_entry.answer}\n",
                    )
                )
            else:  # Other person's message
                # Concatenate the name and content of the other person's message
                conversation.append(
                    UserMessage(
                        role="user",
                        content=f"{chat_entry.answer}\n",
                    )
                )

        return conversation
