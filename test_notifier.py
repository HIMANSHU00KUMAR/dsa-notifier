import sys
import logging
from src.config import get_config
from src.codeforces_client import CodeforcesClient
from src.notifier import NotificationManager
from src.formatter import format_whatsapp_message

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("TestRunner")


def test_codeforces_fetch():
    logger.info("--- Testing DSA Problem Fetching (Dry Run) ---")
    config = get_config()
    client = CodeforcesClient()

    logger.info(f"Using CF Handle: '{config.cf_handle}'")
    if config.cf_handle:
        info = client.get_user_info(config.cf_handle)
        if info:
            logger.info(f"User Info: Rating={info.get('rating')}, Rank={info.get('rank')}, MaxRating={info.get('maxRating')}")
        solved = client.get_user_solved_problems(config.cf_handle)
        logger.info(f"User Solved Count: {len(solved)}")

    problem = client.select_daily_problem(
        handle=config.cf_handle,
        min_rating=config.min_rating,
        max_rating=config.max_rating,
        preferred_tags=config.preferred_tags
    )
    
    logger.info(f"Successfully selected problem: {problem['key']} - {problem['name']} (Rating: {problem['rating']})")
    msg = format_whatsapp_message(problem, handle=config.cf_handle, target_range=problem.get("target_range", ""))
    print("\n" + "="*45)
    print(msg)
    print("="*45 + "\n")
    return problem, msg


def test_notification_dispatch(custom_msg=None, problem_url=None):
    logger.info("--- Testing Notification Dispatch ---")
    config = get_config()
    
    errors = config.validate()
    if errors:
        logger.error(f"Configuration validation failed for channel '{config.notification_channel}':")
        for err in errors:
            logger.error(f"  - {err}")
        return False

    notifier = NotificationManager(config)

    test_message = custom_msg or (
        "🚀 *DSA Daily Notifier - Test Alert* 🚀\n\n"
        "✅ If you are receiving this message, your notification channel is 100% working!\n"
        "Your personalized daily DSA problems will be delivered here every morning. Happy coding! 🎯"
    )

    logger.info(f"Sending test notification via [{config.notification_channel}]...")
    try:
        success = notifier.dispatch(
            message=test_message,
            title="🚀 DSA Daily Notifier - Test Alert",
            url=problem_url or "https://codeforces.com"
        )
        if success:
            logger.info(f"🎉 SUCCESS! Notification dispatched successfully via {config.notification_channel}.")
        else:
            logger.error(f"❌ Failed to send notification via {config.notification_channel}.")
        return success
    except Exception as e:
        logger.exception(f"❌ Error during notification dispatch: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "="*40)
    print("🔥 DSA Daily Notifier - Diagnostic Tool 🔥")
    print("="*40)
    print("1. Test Problem Selection & Formatting (Dry Run)")
    print("2. Test Notification Delivery (Sends a test alert)")
    print("3. Test Full Flow (Fetch real problem & Send alert)")

    if len(sys.argv) > 1:
        choice = sys.argv[1].strip()
    else:
        choice = input("\nEnter choice [1, 2, or 3] (default 1): ").strip() or "1"

    if choice == "1":
        test_codeforces_fetch()
    elif choice == "2":
        test_notification_dispatch()
    elif choice == "3":
        problem, msg = test_codeforces_fetch()
        test_notification_dispatch(custom_msg=msg, problem_url=problem.get("url"))
    else:
        print("Invalid choice. Running dry-run test...")
        test_codeforces_fetch()

