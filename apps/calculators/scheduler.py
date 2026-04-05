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


def collect_mentions_job():
    """Daily job: collect political mentions from BiH media RSS feeds."""
    try:
        from apps.politics.scrapers import run_all_portals
        results = run_all_portals()
        success = sum(1 for r in results if r.get('status') == 'success')
        total_found = sum(r.get('mentions_found', 0) for r in results)
        logger.info(
            'Mentions scrape complete: %d/%d portals OK, %d mentions found',
            success, len(results), total_found,
        )
    except Exception as e:
        logger.exception('Mentions scrape failed: %s', e)


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

    scheduler.add_job(
        collect_mentions_job,
        trigger=CronTrigger(hour=7, minute=0),  # every day at 07:00
        id='collect_mentions_daily',
        name='Collect political mentions from RSS',
        replace_existing=True,
    )

    scheduler.start()
    logger.info('Scheduler started — rates at 06:00, mentions at 07:00 (Sarajevo time)')
