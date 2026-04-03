"""
Interest rate scraper for BiH and Serbian banks.

Run via: python manage.py scrape_rates
"""
import re
import logging

import requests
from bs4 import BeautifulSoup
from django.utils import timezone

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'bs,hr;q=0.9,sr;q=0.8,en;q=0.7',
}
TIMEOUT = 20


def _get(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False)
        resp.raise_for_status()
        resp.encoding = 'utf-8'
        return BeautifulSoup(resp.text, 'lxml')
    except Exception as exc:
        logger.warning('GET %s failed: %s', url, exc)
        return None



def _extract_ert(text):
    """Extract EKS/ERT (effective interest rate) from text."""
    if not text:
        return None
    cleaned = text.replace(',', '.')
    match = re.search(r'EKS[^\d]*(\d+\.\d+)', cleaned, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass
    return None


def _make_offer(loan_type, rate, source_url, text='', currency='BAM', ert=None):
    return {
        'loan_type': loan_type,
        'rate': rate,
        'rate_type': 'fixed',
        'ert': ert or _extract_ert(text),
        'min_amount': None,
        'max_amount': None,
        'min_term_months': None,
        'max_term_months': None,
        'currency': currency,
        'notes': text[:250] if text else '',
        'source_url': source_url,
    }


def _scrape_rates_from_page(url, loan_type, currency='BAM'):
    """Generic scraper: fetch page, find all % values, return first valid rate."""
    soup = _get(url)
    if not soup:
        return None

    full_text = soup.get_text(' ', strip=True)
    # Find all percentage values in the page
    cleaned = full_text.replace(',', '.').replace('\xa0', '')
    matches = re.findall(r'(\d{1,2}\.\d{1,4})%', cleaned)
    for m in matches:
        try:
            val = float(m)
            if 0.5 < val < 30:
                ert = _extract_ert(full_text)
                return _make_offer(loan_type, val, url, full_text[:250], currency, ert)
        except ValueError:
            pass
    return None


# ---------------------------------------------------------------------------
# BiH scrapers
# ---------------------------------------------------------------------------

class UniCreditBHScraper:
    BANK_SHORT = 'unicredit-bh'

    URLS = [
        ('https://www.unicreditbank.ba/home/wps/wcm/connect/ucb_ba/public/retail/loans/housing/', 'stambeni', 'BAM'),
        ('https://www.unicreditbank.ba/home/wps/wcm/connect/ucb_ba/public/retail/loans/cash/', 'gotovinski', 'BAM'),
        ('https://www.unicreditbank.ba/home/wps/wcm/connect/ucb_ba/public/retail/loans/auto/', 'auto', 'BAM'),
    ]

    def scrape(self):
        offers = []
        for url, loan_type, currency in self.URLS:
            offer = _scrape_rates_from_page(url, loan_type, currency)
            if offer:
                offers.append(offer)
        return offers


class RaiffeisenBHScraper:
    BANK_SHORT = 'raiffeisen-bh'

    URLS = [
        ('https://www.raiffeisenbank.ba/bs/stanovnistvo/proizvodi/krediti/stambeni-krediti.html', 'stambeni', 'BAM'),
        ('https://www.raiffeisenbank.ba/bs/stanovnistvo/proizvodi/krediti/nenamjenski-kredit.html', 'gotovinski', 'BAM'),
    ]

    def scrape(self):
        offers = []
        for url, loan_type, currency in self.URLS:
            offer = _scrape_rates_from_page(url, loan_type, currency)
            if offer:
                offers.append(offer)
        return offers


class NLBBHScraper:
    BANK_SHORT = 'nlb-bh'

    URLS = [
        ('https://www.nlb.ba/bs/stanovnistvo/krediti/stambeni-kredit.html', 'stambeni', 'BAM'),
        ('https://www.nlb.ba/bs/stanovnistvo/krediti/gotovinski-kredit.html', 'gotovinski', 'BAM'),
    ]

    def scrape(self):
        offers = []
        for url, loan_type, currency in self.URLS:
            offer = _scrape_rates_from_page(url, loan_type, currency)
            if offer:
                offers.append(offer)
        return offers


class SparkasseBHScraper:
    BANK_SHORT = 'sparkasse-bh'

    URLS = [
        ('https://www.sparkasse.ba/bs/stanovnistvo/krediti/krediti-bez-namjene/Akcijska-ponuda-kredita', 'gotovinski', 'BAM'),
        ('https://www.sparkasse.ba/bs/stanovnistvo/krediti/krediti-bez-namjene/nenamjenski-krediti-za-penzionere', 'penzionerski', 'BAM'),
    ]

    def scrape(self):
        offers = []
        for url, loan_type, currency in self.URLS:
            offer = _scrape_rates_from_page(url, loan_type, currency)
            if offer:
                offers.append(offer)
        return offers


# ---------------------------------------------------------------------------
# Serbian scrapers
# ---------------------------------------------------------------------------

class RaiffeisenSRBScraper:
    BANK_SHORT = 'raiffeisen-rs'

    URLS = [
        ('https://www.raiffeisenbank.rs/sr/stanovnistvo/krediti/stambeni-kredit.html', 'stambeni', 'RSD'),
        ('https://www.raiffeisenbank.rs/sr/stanovnistvo/krediti/kes-kredit.html', 'gotovinski', 'RSD'),
    ]

    def scrape(self):
        offers = []
        for url, loan_type, currency in self.URLS:
            offer = _scrape_rates_from_page(url, loan_type, currency)
            if offer:
                offers.append(offer)
        return offers


class OTPBankSRBScraper:
    BANK_SHORT = 'otp-rs'

    URLS = [
        ('https://www.otpbanka.rs/stanovnistvo/stambeni-krediti/', 'stambeni', 'RSD'),
        ('https://www.otpbanka.rs/stanovnistvo/ponuda-kes-kredita/', 'gotovinski', 'RSD'),
        ('https://www.otpbanka.rs/stanovnistvo/potrosacki-krediti/potrosacki-kredit-na-licu-mesta/', 'potrosacki', 'RSD'),
    ]

    def scrape(self):
        offers = []
        for url, loan_type, currency in self.URLS:
            offer = _scrape_rates_from_page(url, loan_type, currency)
            if offer:
                offers.append(offer)
        return offers


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

SCRAPER_MAP = {
    'unicredit-bh': UniCreditBHScraper,
    'raiffeisen-bh': RaiffeisenBHScraper,
    'nlb-bh': NLBBHScraper,
    'sparkasse-bh': SparkasseBHScraper,
    'raiffeisen-rs': RaiffeisenSRBScraper,
    'otp-rs': OTPBankSRBScraper,
}


def run_scraper_for_bank(bank_obj):
    from .models import InterestRateOffer, ScrapeLog

    short = (bank_obj.short_name or '').lower().strip()
    scraper_class = SCRAPER_MAP.get(short)

    if not scraper_class:
        return ScrapeLog.objects.create(
            bank=bank_obj, status='failed', records_found=0, records_updated=0,
            error_message=f'No scraper for short_name "{short}"',
        )

    try:
        offers = scraper_class().scrape()
        now = timezone.now()
        updated = 0
        for offer_data in offers:
            InterestRateOffer.objects.update_or_create(
                bank=bank_obj,
                loan_type=offer_data['loan_type'],
                currency=offer_data.get('currency', 'BAM'),
                defaults={
                    'rate': offer_data['rate'],
                    'rate_type': offer_data.get('rate_type', 'fixed'),
                    'ert': offer_data.get('ert'),
                    'min_amount': offer_data.get('min_amount'),
                    'max_amount': offer_data.get('max_amount'),
                    'min_term_months': offer_data.get('min_term_months'),
                    'max_term_months': offer_data.get('max_term_months'),
                    'notes': offer_data.get('notes', ''),
                    'source_url': offer_data.get('source_url', ''),
                    'scraped_at': now,
                    'is_active': True,
                },
            )
            updated += 1

        return ScrapeLog.objects.create(
            bank=bank_obj,
            status='success' if offers else 'partial',
            records_found=len(offers),
            records_updated=updated,
        )
    except Exception as exc:
        logger.exception('Scraper failed for %s', bank_obj.name)
        return ScrapeLog.objects.create(
            bank=bank_obj, status='failed', records_found=0, records_updated=0,
            error_message=str(exc),
        )


def run_all_scrapers():
    from .models import Bank
    results = []
    for bank in Bank.objects.filter(is_active=True):
        log = run_scraper_for_bank(bank)
        results.append(log)
        logger.info('%s: %s (%d found)', bank.name, log.status, log.records_found)
    return results
