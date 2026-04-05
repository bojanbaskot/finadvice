"""
Management command: collect_mentions
Scrapes all active media portals for political mentions.

Usage:
    python manage.py collect_mentions
    python manage.py collect_mentions --portal klix.ba
    python manage.py collect_mentions --dry-run
"""
from django.core.management.base import BaseCommand

from apps.politics.scrapers import run_all_portals, scrape_portal


class Command(BaseCommand):
    help = 'Collect political mentions from RSS feeds of BiH media portals'

    def add_arguments(self, parser):
        parser.add_argument(
            '--portal',
            type=str,
            default=None,
            help='Scrape only portals whose URL contains this string (e.g. klix.ba)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            default=False,
            help='Parse feeds but do not write to DB',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        portal_filter = options['portal']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN — no changes will be saved'))

        if portal_filter:
            from apps.politics.models import MediaPortal, PoliticalFigure, PoliticalParty
            portals = MediaPortal.objects.filter(
                is_active=True, url__icontains=portal_filter
            ).exclude(rss_url='')
            if not portals.exists():
                self.stderr.write(f'No active portals found matching "{portal_filter}"')
                return
            figures = list(PoliticalFigure.objects.filter(is_active=True).select_related('party'))
            parties = list(PoliticalParty.objects.filter(is_active=True))
            for portal in portals:
                result = scrape_portal(portal, figures, parties, dry_run=dry_run)
                self._print_result(result, portal.name)
        else:
            results = run_all_portals(dry_run=dry_run)
            for result in results:
                self._print_result(result, result.get('portal', '?'))

        self.stdout.write(self.style.SUCCESS('Done.'))

    def _print_result(self, result, portal_name):
        status = result.get('status', '')
        checked = result.get('articles_checked', 0)
        found = result.get('mentions_found', 0)
        err = result.get('error_message', '')

        style = self.style.SUCCESS if status == 'success' else (
            self.style.WARNING if status == 'partial' else self.style.ERROR
        )
        msg = f'{portal_name}: {status or "?"} ({checked} checked, {found} found)'
        if err:
            msg += f' — {err}'
        self.stdout.write(style(msg))
