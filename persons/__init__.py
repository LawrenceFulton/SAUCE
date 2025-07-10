from __future__ import annotations
import warnings
warnings.filterwarnings("ignore")

from typing import Type
from functools import cache

from dotenv import load_dotenv

import persons.fake_person
import persons.person
import persons.human
import persons.person_gpt3_5
import persons.person_openai_completion
import persons.person_open_router_completion
import persons.person_vllm
import persons.asynchronous_persons.async_human
from .batch import get_batch_dict

load_dotenv()


@cache  # adding cache avoid creating the dict again and again, but still make it read only
def __generate_person_dict():
    return {
        persons.person_open_router_completion.PersonOpenRouterCompletion.PERSON_TYPE: persons.person_open_router_completion.PersonOpenRouterCompletion,
        persons.fake_person.FakePerson.PERSON_TYPE: persons.fake_person.FakePerson,
        persons.human.Human.PERSON_TYPE: persons.human.Human,
        persons.person_gpt3_5.Person3_5.PERSON_TYPE: persons.person_gpt3_5.Person3_5,
        persons.person_openai_completion.PersonOpenAiCompletion.PERSON_TYPE: persons.person_openai_completion.PersonOpenAiCompletion,
        persons.person_vllm.PersonVLLM.PERSON_TYPE: persons.person_vllm.PersonVLLM,
        persons.asynchronous_persons.async_human.AsynchronousHuman.PERSON_TYPE: persons.asynchronous_persons.async_human.AsynchronousHuman,
        **get_batch_dict(),
    }


@cache # reduce the loading time the user was already reloaded
def get_person_class(name: str) -> Type[persons.person.Person]:
    _dict = __generate_person_dict()
    return _dict.get(name)
