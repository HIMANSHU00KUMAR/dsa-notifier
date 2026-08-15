import logging
import sys
import os

from src.config import get_config
from src.codeforces_client import CodeforcesClient
from src.history_manager import HistoryManager
from src.formatter import format_whatsapp_message
from src.notifier import NotificationManager

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("DSANotifier")


def run():
    logger.info("=== Starting Daily DSA Problem Job ===")
    config = get_config()

    # Validate configuration
    validation_errors = config.validate()
    if validation_errors:
        logger.error("Configuration validation failed:")
        for err in validation_errors:
            logger.error(f"  - {err}")
        logger.error("Please configure the required environment variables in your .env file or GitHub Secrets.")
        sys.exit(1)

    # Initialize components
    history_mgr = HistoryManager(config.history_file)
    cf_client = CodeforcesClient()
    notifier = NotificationManager(config)

    # 1. Fetch excluded past problem keys
    excluded_keys = history_mgr.get_excluded_keys()
    logger.info(f"Loaded {len(excluded_keys)} previously sent problems from history.")

    # 2. Select daily problem
    try:
        problem = cf_client.select_daily_problem(
            handle=config.cf_handle,
            min_rating=config.min_rating,
            max_rating=config.max_rating,
            preferred_tags=config.preferred_tags,
            excluded_keys=excluded_keys
        )
    except Exception as e:
        logger.exception(f"Failed to select daily DSA problem: {e}")
        sys.exit(1)

    logger.info(f"Selected Problem: {problem['key']} - {problem['name']} (Rating: {problem['rating']})")

    # 3. Format message
    target_range = problem.get("target_range", "")
    message = format_whatsapp_message(
        problem=problem,
        handle=config.cf_handle,
        target_range=target_range
    )
    print("\n--- Message Preview ---")
    print(message)
    print("-------------------------\n")

    # 4. Dispatch Notification
    try:
        title = f"🎯 DSA Daily: {problem['key']} - {problem['name']} (★ {problem['rating']})"
        success = notifier.dispatch(message, title=title, url=problem.get("url"))
        if not success:
            logger.error(f"Failed to send notification via {config.notification_channel}.")
            sys.exit(1)
    except Exception as e:
        logger.exception(f"Error while dispatching notification: {e}")
        sys.exit(1)

    # 5. Record to history
    try:
        history_mgr.record_problem(problem)
    except Exception as e:
        logger.warning(f"Problem notification sent, but failed to update history file: {e}")

    logger.info("=== Daily DSA Problem Job Completed Successfully! ===")


if __name__ == "__main__":
    run()
