"""
RSS-based scraper for BiH media portals.
Collects articles mentioning political figures/parties and performs sentiment analysis.
Uses feedparser — no heavy dependencies.
"""
import logging
from datetime import datetime, timezone

import feedparser

from .sentiment import analyze_sentiment, extract_mention_excerpt

logger = logging.getLogger(__name__)


def _parse_date(entry):
    """Extract a timezone-aware datetime from a feedparser entry."""
    # feedparser normalises published_parsed to UTC struct_time
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
        return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
    return datetime.now(tz=timezone.utc)


def _entry_text(entry):
    """Return the best available text for sentiment / mention analysis."""
    parts = []
    if getattr(entry, 'title', None):
        parts.append(entry.title)
    # feedparser exposes summary / content
    if getattr(entry, 'summary', None):
        parts.append(entry.summary)
    if getattr(entry, 'content', None):
        for c in entry.content:
            if c.get('value'):
                parts.append(c['value'])
    return ' '.join(parts)


def _strip_html(text):
    """Very lightweight HTML tag removal — avoids BeautifulSoup dependency."""
    import re
    return re.sub(r'<[^>]+>', ' ', text)


def scrape_portal(portal, figures, parties, dry_run=False):
    """
    Scrape one MediaPortal's RSS feed and create PoliticalMention records.

    Args:
        portal: MediaPortal instance
        figures: queryset/list of active PoliticalFigure instances
        parties: queryset/list of active PoliticalParty instances
        dry_run: if True, parse but do not write to DB

    Returns:
        dict with articles_checked, mentions_found, error_message
    """
    # Avoid circular imports — models imported lazily
    from .models import PoliticalMention, MentionScrapeLog

    if not portal.rss_url:
        return {'articles_checked': 0, 'mentions_found': 0, 'error_message': 'No RSS URL configured'}

    # Build lookup: name_variant (lowercase) -> (figure, [all_variants])
    figure_lookup = {}
    for fig in figures:
        for variant in fig.get_name_list():
            figure_lookup[variant.lower()] = fig

    party_lookup = {}
    for party in parties:
        variants = [party.name.lower(), party.abbreviation.lower()] if party.abbreviation else [party.name.lower()]
        for variant in variants:
            party_lookup[variant] = party

    try:
        feed = feedparser.parse(portal.rss_url)
    except Exception as exc:
        return {'articles_checked': 0, 'mentions_found': 0, 'error_message': str(exc)}

    if feed.bozo and not feed.entries:
        err = str(getattr(feed, 'bozo_exception', 'Feed parse error'))
        return {'articles_checked': 0, 'mentions_found': 0, 'error_message': err}

    articles_checked = 0
    mentions_found = 0

    for entry in feed.entries:
        articles_checked += 1

        url = getattr(entry, 'link', None)
        if not url:
            continue

        title = getattr(entry, 'title', '')
        raw_text = _strip_html(_entry_text(entry))
        article_date = _parse_date(entry)

        # One mention per article URL — figure takes priority over party
        matched_figure = None
        matched_party = None

        for variant_lower, figure in figure_lookup.items():
            if variant_lower in raw_text.lower():
                matched_figure = (variant_lower, figure)
                break

        if not matched_figure:
            for variant_lower, party in party_lookup.items():
                if variant_lower in raw_text.lower():
                    matched_party = (variant_lower, party)
                    break

        if matched_figure:
            variant_lower, figure = matched_figure
            name_variants = figure.get_name_list()
            excerpt = extract_mention_excerpt(raw_text, name_variants)
            score, label = analyze_sentiment(raw_text)

            if not dry_run:
                _, created = PoliticalMention.objects.get_or_create(
                    article_url=url,
                    defaults={
                        'portal': portal,
                        'figure': figure,
                        'party': figure.party,
                        'article_title': title[:500],
                        'article_date': article_date,
                        'excerpt': excerpt,
                        'sentiment_score': score,
                        'sentiment_label': label,
                        'mention_count': raw_text.lower().count(variant_lower),
                    }
                )
                if created:
                    mentions_found += 1
            else:
                mentions_found += 1

        elif matched_party:
            variant_lower, party = matched_party
            excerpt = extract_mention_excerpt(raw_text, [party.name, party.abbreviation or ''])
            score, label = analyze_sentiment(raw_text)

            if not dry_run:
                _, created = PoliticalMention.objects.get_or_create(
                    article_url=url,
                    defaults={
                        'portal': portal,
                        'figure': None,
                        'party': party,
                        'article_title': title[:500],
                        'article_date': article_date,
                        'excerpt': excerpt,
                        'sentiment_score': score,
                        'sentiment_label': label,
                        'mention_count': raw_text.lower().count(variant_lower),
                    }
                )
                if created:
                    mentions_found += 1
            else:
                mentions_found += 1

    return {
        'articles_checked': articles_checked,
        'mentions_found': mentions_found,
        'error_message': '',
    }


def run_all_portals(dry_run=False):
    """
    Scrape all active portals with an RSS URL.
    Updates portal.last_scraped and portal.articles_collected.
    Creates MentionScrapeLog entries.
    Returns list of result dicts.
    """
    from django.utils import timezone as dj_timezone
    from .models import MediaPortal, PoliticalFigure, PoliticalParty, MentionScrapeLog

    portals = MediaPortal.objects.filter(is_active=True).exclude(rss_url='')
    figures = list(PoliticalFigure.objects.filter(is_active=True).select_related('party'))
    parties = list(PoliticalParty.objects.filter(is_active=True))

    results = []
    for portal in portals:
        logger.info(f'Scraping portal: {portal.name}')
        result = scrape_portal(portal, figures, parties, dry_run=dry_run)

        status = 'success'
        if result['error_message']:
            status = 'failed' if result['articles_checked'] == 0 else 'partial'
        elif result['mentions_found'] == 0 and result['articles_checked'] > 0:
            status = 'partial'

        if not dry_run:
            MentionScrapeLog.objects.create(
                portal=portal,
                status=status,
                articles_checked=result['articles_checked'],
                mentions_found=result['mentions_found'],
                error_message=result['error_message'],
            )
            portal.last_scraped = dj_timezone.now()
            portal.articles_collected += result['articles_checked']
            portal.save(update_fields=['last_scraped', 'articles_collected'])

        result['portal'] = portal.name
        result['status'] = status
        results.append(result)
        logger.info(
            f'  {portal.name}: {status} '
            f'({result["articles_checked"]} checked, {result["mentions_found"]} found)'
        )

    return results
