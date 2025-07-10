from __future__ import annotations
from typing import Type
from functools import cache
from .batch_person import BatchedPerson


@cache
def get_batch_dict() -> dict[str, Type[BatchedPerson]]:
    return {
    }
