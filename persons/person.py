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
        This implementation always returns a single system message (one-item list) where
        previously separate messages are joined with newline characters.
        """

        # Build the pieces of the single system message depending on prompt_version
        parts: List[str] = []

        if prompt_version == "v0":
            content = f"Scenario: {experiment_scenario}\n"
            if is_questionnaire:
                if self.background_story:
                    content += f"Background Story: {self.background_story}\n"
                content += "The following is a a debate between you and another person\n"
            else:
                if self.background_story:
                    content += f"Background Story: {self.background_story}\n"
                content += (
                    "The following is a debate between you and and another person. "
                    "Complete your next reply. Keep the reply shorter than 30 words.\n"
                )
            parts.append(content)

        elif prompt_version == "v1":
            parts.append(f"The scenario is the following: {experiment_scenario}")
            if self.background_story:
                parts.append(f"This is your background story: {self.background_story}")
            if is_questionnaire:
                parts.append("The following is a conversation between you and another person.")
            else:
                parts.append(
                    "The following is a conversation between you and another person. "
                    "Complete your next reply. Don't make your answers too long.\n"
                )

        elif prompt_version == "v2":
            # Keep the original ordering: instructions first, then scenario, then background (if any)
            if is_questionnaire:
                parts.append(
                    "Kindly respond to the next message from another person. "
                    "Please reply with only a number."
                )
            else:
                parts.append(
                    "You are about to have a conversation with another person. "
                    "Kindly respond to the next message from another person. "
                    "Please keep your reply under 30 words."
                )
            parts.append(f"Please imagine the following scenario: {experiment_scenario}")
            if self.background_story:
                parts.append(f"Here is your background: {self.you_background_story}")

        else:
            raise AssertionError(f"Unknown prompt version {prompt_version}. Please use v0, v1 or v2.")

        # Join all non-empty parts with newline characters and return as single system message
        single_system: ChatCompletionSystemMessageParam = {
            "role": "system",
            "content": "\n".join([p for p in parts if p and p.strip() != ""]),
        }

        return [single_system]
