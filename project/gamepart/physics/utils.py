import logging
import sys
import io

# suppress pymunk import info
sys.stdout = io.StringIO()
import pymunk  # noqa

sys.stdout = sys.__stdout__
logging.info("pymunk %s with chipmunk %s", pymunk.version, pymunk.chipmunk_version)
