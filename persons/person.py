from __future__ import annotations

import copy
import logging
from abc import ABC, abstractmethod
from typing import Any, Tuple, List, Union, Literal
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionSystemMessageParam

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
    def generate_answer(self, experiment_scenario: str, chat_list: List[ChatEntry], prompt_version: str
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
            'person_type': self.PERSON_TYPE,
            'background_story': self.background_story,
            'name': self.name
        }


    def prompt_setups(self, prompt_version: Literal["v0", "v1", "v2"], experiment_scenario: str) -> List[ChatCompletionMessageParam]:
        """
        Returns the prompt setup for the given version.
        """
        if prompt_version == "v0":
            name_message: ChatCompletionSystemMessageParam = {
                "role": "system",
                "content": f"Your name is {self.name}.",
            }
            scenario_message: ChatCompletionSystemMessageParam = {
                "role": "system",
                "content": f"The scenario is the following: {experiment_scenario}",
            }
            system_message: ChatCompletionSystemMessageParam = {
                "role": "system",
                "content": f"This is your background story: {self.background_story}",
            }
            general_instructions: ChatCompletionSystemMessageParam = {
                "role": "system",
                "content": "The following is a debate between you and and another person. Complete your next reply. Try to keep the reply shorter than 30 words and in German.\n\n",
            }
            conversation: List[ChatCompletionMessageParam] = [
                general_instructions,
                name_message,
                scenario_message,
                system_message,
            ]

        elif prompt_version == "v1":
            name_message: ChatCompletionSystemMessageParam = {
                "role": "system",
                "content": f"Your name is {self.name}.",
            }
            scenario_message: ChatCompletionSystemMessageParam = {
                "role": "system",
                "content": f"The scenario is the following: {experiment_scenario}",
            }
            system_message: ChatCompletionSystemMessageParam = {
                "role": "system",
                "content": f"This is your background story: {self.background_story}",
            }
            general_instructions: ChatCompletionSystemMessageParam = {
                "role": "system",
                "content": "The following is a conversation between you and and another person. Complete your next reply. Try to keep the reply shorter than 30 words and in German.\n",
            }

            # different order of messages in v1 to v0
            conversation: List[ChatCompletionMessageParam] = [
                name_message,
                scenario_message,
                system_message,
                general_instructions,
            ]

        elif prompt_version == "v2":
            name_message: ChatCompletionSystemMessageParam = {
                "role": "system",
                "content": f"Dein Name ist {self.name}.",
            }
            scenario_message: ChatCompletionSystemMessageParam = {
                "role": "system",
                "content": f"Das Szenario ist das folgende: {experiment_scenario}",
            }
            system_message: ChatCompletionSystemMessageParam = {
                "role": "system",
                "content": f"Dies ist deine Vorgeschichte: {self.background_story}",
            }
            general_instructions: ChatCompletionSystemMessageParam = {
                "role": "system",
                "content": "Es folgt ein Gespräch zwischen Ihnen und einem anderen Person. Vervollständigen Sie Ihre nächste Antwort. Versuchen Sie, die Antwort kürzer als 30 Wörter und in Deutsch zu halten.\n\n",
            }
            conversation: List[ChatCompletionMessageParam] = [
                general_instructions,
                name_message,
                scenario_message,
                system_message,
            ]

        else:
            assert (
                False
            ), f"Unknown prompt version {prompt_version}. Please use v0, v1 or v2."

        return conversation