from main import main
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    try:
        logger.info("Starting lambda function")
        print("Starting lambda function")
        return main(logger)
    except Exception as e:
        logger.error(e)
        raise e

