import logging
import sys
import io

# suppress pymunk import info
import pymunkoptions

pymunkoptions.options["debug"] = False
sys.stdout = io.StringIO()
import pymunk  # noqa

sys.stdout = sys.__stdout__
logging.info("pymunk %s with chipmunk %s", pymunk.version, pymunk.chipmunk_version)


def make_body(
    mass: float = 0, moment: float = 0, body_type: int = pymunk.Body.DYNAMIC, **kwargs
) -> pymunk.Body:
    body = pymunk.Body(mass, moment, body_type)
    for key, value in kwargs:
        setattr(body, key, value)
    return body


def update_shape(shape: pymunk.Shape, **kwargs) -> pymunk.Shape:
    for key, value in kwargs:
        setattr(shape, key, value)
    return shape
