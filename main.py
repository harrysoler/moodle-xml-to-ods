import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

from returns import methods, pointfree
from returns.curry import curry
from returns.functions import tap
from returns.maybe import Maybe, Nothing, Some
from returns.pipeline import flow, is_successful
from returns.pointfree import bind, bind_optional

NUMBER_OF_ANSWERS: int = 4

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

# limit how much items a list can have
@curry
def with_n_items[T](length: int, items: list[T]) -> Maybe[list[T]]:
    return methods.cond(
        Maybe,
        len(items) == length,
        items
    )

def flatten_list_of_somethings[T](items: list[Some[T]]) -> Maybe[list[T]]:
    return flow(
        map(lambda item: is_successful(item), items),
        lambda items_are_something: all(items_are_something),
        pointfree.cond(Maybe, list(map(lambda item: item.unwrap(), items)))
    )

@curry
def warn_if_missing_tag(tag: Tag, element: Maybe[ET.Element]) -> None:
    element.or_else_call(lambda: logging.warning(f"Element <{tag}> not found"))

def warn_if_answers_quantity_dont_match(answers: Maybe[list[ET.Element]]) -> None:
    if answers == Nothing:
        logging.warning(f"Answers quantity not compliant want {NUMBER_OF_ANSWERS}")

@curry
def get_child_with_tag(tag: Tag, element: ET.Element) -> Maybe[ET.Element]:
    logging.debug(f"get_child_with_tag: Reading {element} for tag '{tag}'")

    return tap(warn_if_missing_tag(tag))(
        Maybe.from_optional(element.find('./' + tag))
    )

@curry
def get_childs_with_tag(tag: Tag, element: ET.Element) -> Maybe[list[ET.Element]]:
    logging.debug(f"get_childs_with_tag: Reading {element} for tags '{tag}'")

    return tap(warn_if_missing_tag(tag))(
        Maybe.from_optional(element.findall('./' + tag))
    )

# when tags have a <text> child, get directly their value
def get_element_sub_text(element: ET.Element) -> Maybe[str]:
    logging.debug(f"get_element_sub_text: Reading {element}")

    return flow(
        element,
        get_child_with_tag(Tag.TEXT),
        bind_optional(lambda element: element.text.strip())
    )

def get_child_tag_sub_text(tag: Tag, element: ET.Element) -> Maybe[str]:
    logging.debug(f"get_child_tag_sub_text: Reading {element} for tag '{tag}'")

    return flow(
        element,
        get_child_with_tag(tag),
        bind(get_element_sub_text)
    )

def element_to_answer(element: ET.Element) -> Maybe[Answer]:
    logging.debug(f"element_to_answer: Reading {element}")

    if element.tag != Tag.ANSWER:
        return Nothing

    return Maybe.do(
        Answer(text, feedback)
        for text in get_element_sub_text(element)
        for feedback in get_child_tag_sub_text(Tag.FEEDBACK, element)
    )

def extract_answers(element: ET.Element) -> Maybe[Answers]:
    logging.debug(f"extract_answers: Reading {element}")

    return flow(
        element,
        get_childs_with_tag(Tag.ANSWER),
        # check if are number of answers required or nothing
        bind(with_n_items(NUMBER_OF_ANSWERS)),
        tap(warn_if_answers_quantity_dont_match),
        bind(lambda answers: map(element_to_answer, answers)),
        flatten_list_of_somethings,
        bind_optional(tuple)
    )

def element_to_question(element: ET.Element) -> Maybe[Question]:
    logging.debug(f"element_to_question: Reading {element}")

    if element.tag != Tag.QUESTION:
        return Nothing

    return Maybe.do(
        Question(name, text, answers)
        for name in get_child_tag_sub_text(Tag.NAME, element)
        for text in get_child_tag_sub_text(Tag.QUESTION_TEXT, element)
        for answers in extract_answers(element)
    )

def extract_questions(element: ET.Element) -> Maybe[list[Question]]:
    logging.debug(f"extract_questions: Reading {element}")

    return flow(
        element,
        get_childs_with_tag(Tag.QUESTION),
        bind(lambda questions: map(element_to_question, questions)),
        flatten_list_of_somethings
    )

def main():
    tree = ET.parse("./desarrollo_orientado_a_servicios.xml")
    root = tree.getroot()

    # logging.getLogger().setLevel(logging.DEBUG)

    questions = extract_questions(root)
    print(questions)

if __name__ == "__main__":
    main()


            
