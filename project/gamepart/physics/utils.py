import functools
import logging
import typing

import pymunk

logging.info("pymunk %s with chipmunk %s", pymunk.version, pymunk.chipmunk_version)


def make_body(
    mass: float = 0,
    moment: float = 0,
    body_type: int = pymunk.Body.DYNAMIC,
    **kwargs: typing.Any,
) -> pymunk.Body:
    body = pymunk.Body(mass, moment, body_type)
    for key, value in kwargs.items():
        setattr(body, key, value)
    return body


def update_shape(shape: pymunk.Shape, **kwargs: typing.Any) -> pymunk.Shape:
    for key, value in kwargs.items():
        setattr(shape, key, value)
    return shape


def typed_property(rtype: type) -> typing.Callable[..., property]:
    @functools.wraps(property)
    def prop(*args: typing.Any, **kwargs: typing.Any) -> property:
        return property(*args, **kwargs)

    prop.__annotations__["return"] = rtype
    return prop
