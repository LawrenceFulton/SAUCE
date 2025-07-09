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

    def __init__(self, background_story: str, name: str, *args, **kwargs):
        self.background_story: str = background_story
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
        if prompt_version == "v0":

            if is_questionnaire:
                scenario_message: ChatCompletionSystemMessageParam = {
                    "role": "system",
                    "content": f"Scenario: {experiment_scenario}\nBackground Story: {self.background_story}\nThe following is a a debate between you and another person\n"
                }
            else: 
                scenario_message: ChatCompletionSystemMessageParam = {
                    "role": "system",
                    "content": f"Scenario: {experiment_scenario}\nBackground Story: {self.background_story}\nThe following is a debate between you and and another person. Complete your next reply. Keep the reply shorter than 30 words and in German.\n\n",
                }

            conversation: List[ChatCompletionMessageParam] = [
                scenario_message,
            ]

        elif prompt_version == "v1":

            scenario_message: ChatCompletionSystemMessageParam = {
                "role": "system",
                "content": f"The scenario is the following: {experiment_scenario}",
            }
            system_message: ChatCompletionSystemMessageParam = {
                "role": "system",
                "content": f"This is your background story: {self.background_story}",
            }
            if is_questionnaire:
                general_instructions: ChatCompletionSystemMessageParam = {
                    "role": "system",
                    "content": "The following is a conversation between you and another person.",
                }

            else:
                general_instructions: ChatCompletionSystemMessageParam = {
                    "role": "system",
                    "content": "The following is a conversation between you and another person. Complete your next reply. Keep the reply shorter than 30 words and in German.\n",
                }

            conversation: List[ChatCompletionMessageParam] = [
                scenario_message,
                system_message,
                general_instructions,
            ]

        elif prompt_version == "v2":
            # New English prompt structure for v2
            scenario_message: ChatCompletionSystemMessageParam = {
                "role": "system",
                "content": f"Scenario: {experiment_scenario}",
            }
            background_message: ChatCompletionSystemMessageParam = {
                "role": "system",
                "content": f"Background Story: {self.background_story}",
            }
            if is_questionnaire:
                instructions_message: ChatCompletionSystemMessageParam = {
                    "role": "system",
                    "content": (
                        "You are about to have a conversation with another person."
                        "Please reply with only a number."
                    ),
                }
            else:
                instructions_message: ChatCompletionSystemMessageParam = {
                    "role": "system",
                    "content": (
                        "You are about to have a conversation with another person. "
                        "Respond to the next message. Please keep your reply under 30 words and in German."
                    ),
                }
            conversation: List[ChatCompletionMessageParam] = [
                instructions_message,
                scenario_message,
                background_message,
            ]

        else:
            assert (
                False
            ), f"Unknown prompt version {prompt_version}. Please use v0, v1 or v2."

        return conversation
