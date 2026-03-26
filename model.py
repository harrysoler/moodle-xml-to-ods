from constant import NUMBER_OF_ANSWERS
from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

class Tag(StrEnum):
    NAME = "name"
    TEXT = "text"
    QUESTION = "question"
    QUESTION_TEXT = "questiontext"
    ANSWER = "answer"
    FEEDBACK = "feedback"

@dataclass
class Answer(object):
    text: str
    feedback: str

    def __post_init__(self):
        if len(self.text) == 0:
            raise ValueError("The answer text cannot be empty")

Answers: TypeAlias = tuple[(Answer,) * NUMBER_OF_ANSWERS]

@dataclass
class Question(object):
    title: str
    text: str
    answers: Answers
