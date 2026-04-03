from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
import logging

logger = logging.getLogger(__name__)


def scrape_rates_job():
    """Daily job: scrape interest rates from all active banks."""
    try:
        from apps.calculators.scraper import run_all_scrapers
        results = run_all_scrapers()
        success = sum(1 for r in results if r.status == 'success')
        logger.info('Scheduled scrape complete: %d/%d banks successful', success, len(results))
    except Exception as e:
        logger.exception('Scheduled scrape failed: %s', e)


def start():
    scheduler = BackgroundScheduler(timezone='Europe/Sarajevo')
    scheduler.add_jobstore(DjangoJobStore(), 'default')

    scheduler.add_job(
        scrape_rates_job,
        trigger=CronTrigger(hour=6, minute=0),  # every day at 06:00
        id='scrape_rates_daily',
        name='Scrape bank interest rates',
        replace_existing=True,
    )

    scheduler.start()
    logger.info('Scheduler started — rates will be scraped daily at 06:00')
