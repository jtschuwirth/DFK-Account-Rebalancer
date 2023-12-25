from main import main
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    try:
        logger.info("Starting lambda function")
        return "Running"
        return main(event, context, logger)
    except Exception as e:
        logger.error(e)
        raise e

