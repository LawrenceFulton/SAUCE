from __future__ import annotations

import copy
import logging
from abc import ABC, abstractmethod
from typing import Any, Tuple, List, Union, Literal, Optional
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
)

# protect cyclic imports caused from typing
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from session_rooms.ChatEntry import ChatEntry

log = logging.getLogger(__name__)


class Person(ABC):
    PERSON_TYPE = None

    def __init__(self, background_story: str, you_background_story: str, name: str, *args, **kwargs):
        self.background_story: str = background_story
        self.you_background_story: str = you_background_story
        self.name: str = name

    @abstractmethod
    def generate_answer(
        self,
        experiment_scenario: str,
        chat_list: List[ChatEntry],
        prompt_version: str,
        is_questionnaire: bool = False,
    ) -> Union[ChatEntry, None]:
        """
        Receives the current session state.
        Returns the ChatEntry to be added to the chat, or None if it currently shouldn't add one
        (when using asynchronous communication).
        """
        raise NotImplementedError()

    def __deepcopy__(self, memodict={}):
        log.debug("We don't allow deep copies of person")
        return copy.copy(self)

    def __json__(self):
        """
        return a json serializable representation of the Person instance for serializing using json.dumps
        """
        return {
            "person_type": self.PERSON_TYPE,
            "background_story": self.background_story,
            "name": self.name,
        }

    def prompt_setups(
        self,
        prompt_version: Literal["v0", "v1", "v2"],
        experiment_scenario: str,
        is_questionnaire: bool,
    ) -> List[ChatCompletionMessageParam]:
        """
        Returns the prompt setup for the given version.
        """

        conversation: List[ChatCompletionMessageParam] = []

        ### v0 ###
        if prompt_version == "v0":
            content = f"Scenario: {experiment_scenario}\n"
            if is_questionnaire:
                if self.background_story:
                    content += f"Background Story: {self.background_story}\n"
                content += "The following is a a debate between you and another person\n"
                scenario_message: ChatCompletionSystemMessageParam = {
                    "role": "system",
                    "content": content
                }
            else:
                if self.background_story:
                    content += f"Background Story: {self.background_story}\n"
                content += "The following is a debate between you and and another person. Complete your next reply. Keep the reply shorter than 30 words and in German.\n"
                scenario_message: ChatCompletionSystemMessageParam = {
                    "role": "system",
                    "content": content,
                }
            conversation: List[ChatCompletionMessageParam] = [
                scenario_message,
            ]


        ### v1 ###
        elif prompt_version == "v1":
            scenario_message: ChatCompletionSystemMessageParam = {
                "role": "system",
                "content": f"The scenario is the following: {experiment_scenario}",
            }
            if self.background_story:
                system_message: ChatCompletionSystemMessageParam = {
                    "role": "system",
                    "content": f"This is your background story: {self.background_story}",
                }
            else:
                system_message: ChatCompletionSystemMessageParam = {
                    "role": "system",
                    "content": "",
                }
            if is_questionnaire:
                general_instructions: ChatCompletionSystemMessageParam = {
                    "role": "system",
                    "content": "The following is a conversation between you and another person.",
                }
            else:
                general_instructions: ChatCompletionSystemMessageParam = {
                    "role": "system",
                    "content": "The following is a conversation between you and another person. Complete your next reply. Don't make your answers too long and answer in German.\n",
                }
            conversation: List[ChatCompletionMessageParam] = [
                scenario_message,
            ]
            if self.background_story:
                conversation.append(system_message)
            conversation.append(general_instructions)



        ### v2 ###
        elif prompt_version == "v2":
            scenario_message: ChatCompletionSystemMessageParam = {
                "role": "system",
                "content": f"Please imagine the following scenario: {experiment_scenario}",
            }
            conversation.append(scenario_message)
    
            if self.background_story:
                background_message: ChatCompletionSystemMessageParam = {
                    "role": "system",
                    "content": f"Here is your background: {self.you_background_story}",
                }
                conversation.append(background_message)

            if is_questionnaire:
                instructions_message: ChatCompletionSystemMessageParam = {
                    "role": "system",
                    "content": (
                        "Kindly respond in German to the next message from another person."
                        "Please reply with only a number."
                    ),
                }
            else:
                instructions_message: ChatCompletionSystemMessageParam = {
                    "role": "system",
                    "content": (
                        "You are about to have a conversation with another person. "
                        "Kindly respond in German to the next message from another person. Please keep your reply under 30 words."
                    ),
                }
            conversation.insert(0, instructions_message)

        else:
            assert (
                False
            ), f"Unknown prompt version {prompt_version}. Please use v0, v1 or v2."

        return conversation
