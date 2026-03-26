import logging

from returns import methods, pointfree
from returns.curry import curry
from returns.maybe import Maybe, Nothing, Some
from returns.pipeline import flow, is_successful


# limit how much items a list can have
@curry
def has_n_items_or_nothing[T](length: int, items: list[T]) -> Maybe[list[T]]:
    return methods.cond(
        Maybe,
        len(items) == length,
        items
    )

def maybes_to_list_or_nothing[T](items: list[Some[T]]) -> Maybe[list[T]]:
    return flow(
        map(lambda item: is_successful(item), items),
        lambda items_are_something: all(items_are_something),
        pointfree.cond(Maybe, list(map(lambda item: item.unwrap(), items)))
    )

def warn_if_list_is_nothing[T](items: Maybe[list[T]]) -> None:
    if items == Nothing:
        logging.warning("Generated list is empty")
