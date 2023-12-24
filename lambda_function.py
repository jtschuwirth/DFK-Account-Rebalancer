from main import main
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    try:
        return main(event, context, logger)
    except Exception as e:
        logger.error(e)
        raise e

