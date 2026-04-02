"""
Scrape interest rates from BiH and Serbian banks.

Usage:
  python manage.py scrape_rates                  # all active banks
  python manage.py scrape_rates --bank nlb-bh    # one bank by short_name
"""
from django.core.management.base import BaseCommand, CommandError
from apps.calculators.models import Bank
from apps.calculators.scraper import run_scraper_for_bank, run_all_scrapers


class Command(BaseCommand):
    help = 'Scrape interest rates from banks in BiH and Serbia'

    def add_arguments(self, parser):
        parser.add_argument('--bank', type=str, help='short_name of bank to scrape')

    def handle(self, *args, **options):
        bank_short = options.get('bank')
        if bank_short:
            try:
                bank = Bank.objects.get(short_name__iexact=bank_short)
            except Bank.DoesNotExist:
                raise CommandError(f'Bank "{bank_short}" not found.')
            self._print_log(run_scraper_for_bank(bank))
        else:
            self.stdout.write('Scraping all active banks...')
            for log in run_all_scrapers():
                self._print_log(log)
            self.stdout.write(self.style.SUCCESS('Done.'))

    def _print_log(self, log):
        style = (self.style.SUCCESS if log.status == 'success'
                 else self.style.WARNING if log.status == 'partial'
                 else self.style.ERROR)
        self.stdout.write(style(
            f'  {log.bank.name}: {log.status} '
            f'({log.records_found} found, {log.records_updated} updated)'
        ))
        if log.error_message:
            self.stdout.write(self.style.ERROR(f'    Error: {log.error_message}'))
