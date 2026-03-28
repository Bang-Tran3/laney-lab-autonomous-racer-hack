from training import start_training
from environment import load_environment
from logging_config import get_logger

logger = get_logger("main")

def run_demo():
    logger.info("Starting DeepRacer demo")
    load_environment()
    start_training()

    # Manual test trigger
    failure_message = "ERROR: TEST FAILURE - simulator crashed"
    logger.error(failure_message)

if __name__ == "__main__":
    run_demo()
