import logging
import xml.etree.ElementTree as ET

from returns.curry import curry
from returns.functions import tap
from returns.maybe import Maybe, Nothing
from returns.pipeline import flow
from returns.pointfree import bind, bind_optional, map_

from constant import NUMBER_OF_ANSWERS
from helper import (
    has_n_items_or_nothing,
    maybes_to_list_or_nothing,
    warn_if_list_is_nothing,
)
from model import Answer, Answers, Question, Tag


@curry
def warn_if_missing_tag(tag: Tag, element: Maybe[ET.Element]) -> None:
    element.or_else_call(lambda: logging.warning(f"Element <{tag}> not found"))

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
def find_element_text(element: ET.Element) -> Maybe[str]:
    logging.debug(f"find_element_text: Reading {element}")

    return flow(
        element,
        get_child_with_tag(Tag.TEXT),
        bind_optional(lambda element: element.text.strip())
    )

def find_child_element_text(child_tag: Tag, element: ET.Element) -> Maybe[str]:
    logging.debug(f"find_child_element_text: Reading {element} for tag '{child_tag}'")

    return flow(
        element,
        get_child_with_tag(child_tag),
        bind(find_element_text)
    )

def element_to_answer(element: ET.Element) -> Maybe[Answer]:
    logging.debug(f"element_to_answer: Reading {element}")

    if element.tag != Tag.ANSWER:
        return Nothing

    return Maybe.do(
        Answer(text, feedback)
        for text in find_element_text(element)
        for feedback in find_child_element_text(Tag.FEEDBACK, element)
    )

def elements_to_answers(elements: list[ET.Element]) -> Maybe[Answers]:
    return flow(
        map(element_to_answer, elements),
        maybes_to_list_or_nothing,
        map_(tuple)
    )

def element_to_question(element: ET.Element) -> Maybe[Question]:
    logging.debug(f"element_to_question: Reading {element}")

    if element.tag != Tag.QUESTION:
        return Nothing

    return Maybe.do(
        Question(name, text, answers)
        for name in find_child_element_text(Tag.NAME, element)
        for text in find_child_element_text(Tag.QUESTION_TEXT, element)
        for answers in extract_answers_from(element)
    )

def elements_to_questions(elements: list[ET.Element]) -> Maybe[list[Question]]:
    return flow(
        map(element_to_question, elements),
        maybes_to_list_or_nothing
    )

def extract_answers_from(element: ET.Element) -> Maybe[Answers]:
    logging.debug(f"extract_answers_from: Reading {element}")

    return flow(
        element,
        get_childs_with_tag(Tag.ANSWER),
        # check if are number of answers required or nothing
        bind(has_n_items_or_nothing(NUMBER_OF_ANSWERS)),
        tap(warn_if_list_is_nothing),
        bind(elements_to_answers)
    )

# all questions must be parsed successfully or nothing
def extract_questions_from(element: ET.Element) -> Maybe[list[Question]]:
    logging.debug(f"extract_questions_from: Reading {element}")

    return flow(
        element,
        get_childs_with_tag(Tag.QUESTION),
        bind(elements_to_questions)
    )
