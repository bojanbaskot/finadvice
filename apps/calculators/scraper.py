"""
Interest rate scraper for BiH and Serbian banks.

Each scraper class implements scrape() returning a list of dicts:
  {loan_type, rate, rate_type, ert, min_amount, max_amount,
   min_term_months, max_term_months, currency, notes, source_url}

Banks covered (BiH): UniCredit BH, Raiffeisen BH, NLB BH, Sparkasse BH
Banks covered (SRB): Raiffeisen RS, OTP Bank RS

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
    'Accept-Language': 'bs,hr;q=0.9,en;q=0.8',
}
TIMEOUT = 15


def _get(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, 'lxml')
    except Exception as exc:
        logger.warning('GET %s failed: %s', url, exc)
        return None


def _extract_rate(text):
    """Extract first decimal number, e.g. '4,50%' -> 4.5"""
    if not text:
        return None
    cleaned = text.replace(',', '.').replace('\xa0', '')
    match = re.search(r'(\d{1,2}\.\d{1,4})', cleaned)
    if match:
        try:
            val = float(match.group(1))
            if 0.5 < val < 30:
                return val
        except ValueError:
            pass
    return None


def _extract_ert(text):
    match = re.search(r'EKS[^\d]*(\d+[,\.]\d+)', text, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1).replace(',', '.'))
        except ValueError:
            pass
    return None


def _make_offer(loan_type, rate, source_url, text='', currency='BAM'):
    return {
        'loan_type': loan_type,
        'rate': rate,
        'rate_type': 'fixed',
        'ert': _extract_ert(text),
        'min_amount': None,
        'max_amount': None,
        'min_term_months': None,
        'max_term_months': None,
        'currency': currency,
        'notes': text[:250],
        'source_url': source_url,
    }


# ---------------------------------------------------------------------------
# BiH scrapers
# ---------------------------------------------------------------------------

class UniCreditBHScraper:
    BANK_SHORT = 'unicredit-bh'

    URLS = [
        ('https://www.unicreditbank.ba/stanovnistvo/krediti/stambeni-kredit/', 'housing'),
        ('https://www.unicreditbank.ba/stanovnistvo/krediti/gotovinski-kredit/', 'consumer'),
        ('https://www.unicreditbank.ba/stanovnistvo/krediti/auto-kredit/', 'auto'),
    ]

    def scrape(self):
        offers = []
        for url, loan_type in self.URLS:
            soup = _get(url)
            if not soup:
                continue
            for el in soup.select('table tr, .rate, [class*="kamat"], [class*="interest"]'):
                text = el.get_text(' ', strip=True)
                rate = _extract_rate(text)
                if rate:
                    offers.append(_make_offer(loan_type, rate, url, text))
                    break
        return offers


class RaiffeisenBHScraper:
    BANK_SHORT = 'raiffeisen-bh'

    URLS = [
        ('https://www.raiffeisenbank.ba/bs/stanovnistvo/krediti/stambeni-krediti/', 'housing'),
        ('https://www.raiffeisenbank.ba/bs/stanovnistvo/krediti/gotovinski-krediti/', 'consumer'),
    ]

    def scrape(self):
        offers = []
        for url, loan_type in self.URLS:
            soup = _get(url)
            if not soup:
                continue
            for el in soup.select('table tr, .product-detail, [class*="rate"], [class*="kamat"]'):
                text = el.get_text(' ', strip=True)
                rate = _extract_rate(text)
                if rate:
                    offers.append(_make_offer(loan_type, rate, url, text))
                    break
        return offers


class NLBBHScraper:
    BANK_SHORT = 'nlb-bh'

    URLS = [
        ('https://www.nlbbanka.ba/stanovnistvo/stambeni-krediti/', 'housing'),
        ('https://www.nlbbanka.ba/stanovnistvo/potrosacki-krediti/', 'consumer'),
    ]

    def scrape(self):
        offers = []
        for url, loan_type in self.URLS:
            soup = _get(url)
            if not soup:
                continue
            for el in soup.select('table tr, .credit-info, [class*="kamat"]'):
                text = el.get_text(' ', strip=True)
                rate = _extract_rate(text)
                if rate:
                    offers.append(_make_offer(loan_type, rate, url, text))
                    break
        return offers


class SparkasseBHScraper:
    BANK_SHORT = 'sparkasse-bh'

    URLS = [
        ('https://www.sparkasse.ba/stanovnistvo/krediti/stambeni-kredit/', 'housing'),
        ('https://www.sparkasse.ba/stanovnistvo/krediti/gotovinski-kredit/', 'consumer'),
    ]

    def scrape(self):
        offers = []
        for url, loan_type in self.URLS:
            soup = _get(url)
            if not soup:
                continue
            for el in soup.select('table tr, .kamatna-stopa, [class*="interest"]'):
                text = el.get_text(' ', strip=True)
                rate = _extract_rate(text)
                if rate:
                    offers.append(_make_offer(loan_type, rate, url, text))
                    break
        return offers


# ---------------------------------------------------------------------------
# Serbian scrapers
# ---------------------------------------------------------------------------

class RaiffeisenSRBScraper:
    BANK_SHORT = 'raiffeisen-rs'

    URLS = [
        ('https://www.raiffeisenbank.rs/stanovnistvo/krediti/stambeni-krediti/', 'housing'),
        ('https://www.raiffeisenbank.rs/stanovnistvo/krediti/gotovinski-krediti/', 'consumer'),
    ]

    def scrape(self):
        offers = []
        for url, loan_type in self.URLS:
            soup = _get(url)
            if not soup:
                continue
            for el in soup.select('table tr, .rate-box, [class*="kamat"]'):
                text = el.get_text(' ', strip=True)
                rate = _extract_rate(text)
                if rate:
                    offers.append(_make_offer(loan_type, rate, url, text, currency='RSD'))
                    break
        return offers


class OTPBankSRBScraper:
    BANK_SHORT = 'otp-rs'

    URLS = [
        ('https://www.otpbanka.rs/stanovnistvo/krediti/stambeni-krediti/', 'housing'),
        ('https://www.otpbanka.rs/stanovnistvo/krediti/gotovinski-krediti/', 'consumer'),
        ('https://www.otpbanka.rs/stanovnistvo/krediti/auto-krediti/', 'auto'),
    ]

    def scrape(self):
        offers = []
        for url, loan_type in self.URLS:
            soup = _get(url)
            if not soup:
                continue
            for el in soup.select('table tr, .credit-rate, [class*="kamat"]'):
                text = el.get_text(' ', strip=True)
                rate = _extract_rate(text)
                if rate:
                    offers.append(_make_offer(loan_type, rate, url, text, currency='RSD'))
                    break
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
                rate_type=offer_data.get('rate_type', 'fixed'),
                currency=offer_data.get('currency', 'BAM'),
                defaults={
                    'rate': offer_data['rate'],
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
