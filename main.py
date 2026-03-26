import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Tuple, TypeAlias
from returns.result import Result, Success, Failure
from returns.maybe import Maybe, Nothing, Some
from returns.pipeline import flow
from returns.pointfree import bind
from returns.curry import curry

NAME_TAG = "name"
TEXT_TAG = "text"
QUESTION_TAG = "question"
QUESTION_TEXT_TAG = "questiontext"

@dataclass
class Answer(object):
    text: str
    feedback: str

    def __post_init__():
        if len(self.text) == 0:
            raise ValueError("The answer text cannot be empty")

Answers: TypeAlias = tuple[Answer, Answer, Answer, Answer]

@dataclass
class Question(object):
    title: str
    text: str
    # answers: Answers

@curry
def get_child_with_tag(tag: str, element: ET.Element) -> Maybe[ET.Element]:
    return Maybe.from_optional(element.find('./' + tag))

def get_element_text(element: ET.Element) -> str:
    return element.text

def extract_question_text_from(element: ET.Element) -> Maybe[str]:
    return flow(
        element,
        get_child_with_tag(QUESTION_TEXT_TAG),
        bind(get_child_with_tag(TEXT_TAG)),
        bind(get_element_text)
    )

def extract_question_name_from(element: ET.Element) -> Maybe[str]:
    return flow(
        element,
        get_child_with_tag(NAME_TAG),
        bind(get_child_with_tag(TEXT_TAG)),
        bind(get_element_text)
    )

@curry
def build_question(name: str, text: str, answers: Answers) -> Maybe[Question]:
    Question(name, text)

def element_to_question(element: ET.Element) -> Maybe[Question]:
    if element.tag != QUESTION_TAG:
        return Nothing

    name: Maybe[str] = extract_question_name_from(element)

    question_text: Maybe[str] = extract_question_text_from(element)

    print(question_text)

def main():
    tree = ET.parse("./test.xml")
    root = tree.getroot()

    question = flow(
        root,
        get_child_with_tag(QUESTION_TAG),
        bind(element_to_question)
    )

if __name__ == "__main__":
    main()


            
