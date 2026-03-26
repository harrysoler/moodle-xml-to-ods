import logging
import xml.etree.ElementTree as ET
from enum import StrEnum
from dataclasses import dataclass
from typing import TypeAlias

from returns.curry import curry
from returns.functions import tap
from returns.maybe import Maybe, Nothing, Some
from returns.pipeline import flow
from returns.pointfree import bind

class Tag(StrEnum):
    NAME = "name"
    TEXT = "text"
    QUESTION = "question"
    QUESTION_TEXT = "questiontext"
    ANSWER = "answer"

@dataclass
class Answer(object):
    text: str
    feedback: str

    def __post_init__(self):
        if len(self.text) == 0:
            raise ValueError("The answer text cannot be empty")

Answers: TypeAlias = tuple[Answer, Answer, Answer, Answer]

@dataclass
class Question(object):
    title: str
    text: str
    # answers: Answers

@curry
def warn_if_missing_tag(tag: Tag, element: Maybe[ET.Element]) -> None:
    element.or_else_call(lambda: logging.warning(f"Element <{tag}> not found"))

@curry
def get_child_with_tag(tag: Tag, element: ET.Element) -> Maybe[ET.Element]:
    return tap(warn_if_missing_tag(tag))(
        Maybe.from_optional(element.find('./' + tag))
    )

@curry
def get_childs_with_tag(tag: Tag, element: ET.Element) -> Maybe[list[ET.Element]]:
    return tap(warn_if_missing_tag(tag))(
        Maybe.from_optional(element.findall('./' + tag))
    )

# when tags have a <text> child, get directly their value
def get_element_sub_text(element: ET.Element) -> Maybe[str]:
    return flow(
        element,
        get_child_with_tag(Tag.TEXT),
    ).bind_optional(lambda element: element.text)

def extract_question_text(element: ET.Element) -> Maybe[str]:
    return flow(
        element,
        get_child_with_tag(Tag.QUESTION_TEXT),
        bind(get_element_sub_text)
    )

def extract_question_name(element: ET.Element) -> Maybe[str]:
    return flow(
        element,
        get_child_with_tag(Tag.NAME),
        bind(get_element_sub_text)
    )

def element_to_question(element: ET.Element) -> Maybe[Question]:
    if element.tag != Tag.QUESTION:
        return Nothing
    
    return Maybe.do(
        Question(name, text)
        for name in extract_question_name(element)
        for text in extract_question_text(element)
    )


def main():
    tree = ET.parse("./test.xml")
    root = tree.getroot()

    question = flow(
        root,
        get_child_with_tag(Tag.QUESTION),
        bind(element_to_question)
    )

    print(question)

if __name__ == "__main__":
    main()


            
