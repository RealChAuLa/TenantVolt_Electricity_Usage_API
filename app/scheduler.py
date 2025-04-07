from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi.logger import logger

from app.config import get_current_time
from app.bill.bill_calculator import calculate_monthly_bills_for_all_products

# Create scheduler instance
scheduler = AsyncIOScheduler()


async def check_for_new_month():
    """
    Function that runs periodically to check if it's the first day of a month
    between 00:00 and 00:10, and if so, calculate bills
    """
    current_time = get_current_time()

    logger.info(f"Scheduler check - Current time: {current_time}")

    # Check if it's the first day of the month (between 00:00 and 00:10)
    if current_time.day == 1 and current_time.hour == 0 and current_time.minute < 10:
        logger.info(f"New month detected! Calculating bills at {current_time}")
        await calculate_monthly_bills_for_all_products()
    else:
        logger.info(
            f"Not time for bill calculation yet. Current day={current_time.day}, hour={current_time.hour}, minute={current_time.minute}")


def start_scheduler():
    """Initialize and start the scheduler"""
    # Run the check every minute to ensure we don't miss the window
    scheduler.add_job(
        check_for_new_month,
        trigger=IntervalTrigger(minutes=1),
        id="check_for_new_month",
        replace_existing=True
    )

    scheduler.start()
    logger.info("Scheduler started. Will check for new month every minute.")


def shutdown_scheduler():
    """Shut down the scheduler"""
    scheduler.shutdown()
    logger.info("Scheduler shut down.")