from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.views.generic import TemplateView, DetailView, ListView
from datetime import timedelta

from .models import (
    PoliticalFigure, PoliticalParty, MediaPortal,
    PoliticalMention, MentionScrapeLog,
)


PERIOD_OPTIONS = {
    'day':   {'days': 1,  'label': 'Danas',    'short': '1d'},
    'week':  {'days': 7,  'label': 'Sedmica',  'short': '7d'},
    'month': {'days': 30, 'label': 'Mjesec',   'short': '30d'},
}


def _period_counts(days):
    """Return (total, pos, neg, neu, rs, fbih) for the given number of days back."""
    since = timezone.now() - timedelta(days=days)
    qs = PoliticalMention.objects.filter(article_date__gte=since)
    total = qs.count()
    pos   = qs.filter(sentiment_label='positive').count()
    neg   = qs.filter(sentiment_label='negative').count()
    rs    = qs.filter(portal__entity='RS').count()
    fbih  = qs.filter(portal__entity='FBiH').count()
    return {'total': total, 'positive': pos, 'negative': neg,
            'neutral': total - pos - neg, 'rs': rs, 'fbih': fbih}


class PoliticsDashboardView(TemplateView):
    template_name = 'politics/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Active period from ?period= query param, default month
        period_key = self.request.GET.get('period', 'month')
        if period_key not in PERIOD_OPTIONS:
            period_key = 'month'
        days = PERIOD_OPTIONS[period_key]['days']
        since = timezone.now() - timedelta(days=days)

        # Pre-compute counts for all three periods (shown as summary row)
        period_stats = {
            key: _period_counts(opt['days'])
            for key, opt in PERIOD_OPTIONS.items()
        }

        # Top figures for selected period
        top_figures = (
            PoliticalFigure.objects.filter(is_active=True)
            .annotate(
                mention_count=Count('mentions', filter=Q(mentions__article_date__gte=since)),
                avg_sentiment=Avg('mentions__sentiment_score', filter=Q(mentions__article_date__gte=since)),
            )
            .filter(mention_count__gt=0)
            .order_by('-mention_count')[:10]
        )

        # Top parties for selected period
        top_parties = (
            PoliticalParty.objects.filter(is_active=True)
            .annotate(
                mention_count=Count('mentions', filter=Q(mentions__article_date__gte=since)),
                avg_sentiment=Avg('mentions__sentiment_score', filter=Q(mentions__article_date__gte=since)),
            )
            .filter(mention_count__gt=0)
            .order_by('-mention_count')[:8]
        )

        # Recent mentions for selected period
        recent_mentions = (
            PoliticalMention.objects.select_related('figure', 'party', 'portal')
            .filter(article_date__gte=since)
            .order_by('-article_date')[:20]
        )

        current = period_stats[period_key]

        ctx.update({
            'top_figures': top_figures,
            'top_parties': top_parties,
            'recent_mentions': recent_mentions,
            'total_mentions': current['total'],
            'positive_count': current['positive'],
            'negative_count': current['negative'],
            'neutral_count':  current['neutral'],
            'rs_mentions':    current['rs'],
            'fbih_mentions':  current['fbih'],
            'since_days': days,
            'period_key': period_key,
            'period_options': PERIOD_OPTIONS,
            'period_stats': period_stats,
            'active_portals': MediaPortal.objects.filter(is_active=True).count(),
            'last_logs': MentionScrapeLog.objects.select_related('portal').order_by('-created_at')[:10],
        })
        return ctx


class FigureDetailView(DetailView):
    model = PoliticalFigure
    template_name = 'politics/figure_detail.html'
    context_object_name = 'figure'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        figure = self.object
        since = timezone.now() - timedelta(days=90)

        mentions = (
            figure.mentions.select_related('portal')
            .filter(article_date__gte=since)
            .order_by('-article_date')
        )

        sentiment_by_portal = (
            mentions.values('portal__name', 'portal__entity')
            .annotate(count=Count('id'), avg_score=Avg('sentiment_score'))
            .order_by('-count')
        )

        ctx.update({
            'mentions': mentions[:30],
            'total_mentions': mentions.count(),
            'avg_sentiment': mentions.aggregate(avg=Avg('sentiment_score'))['avg'],
            'sentiment_by_portal': sentiment_by_portal,
            'since_days': 90,
        })
        return ctx


class PartyDetailView(DetailView):
    model = PoliticalParty
    template_name = 'politics/party_detail.html'
    context_object_name = 'party'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        party = self.object
        since = timezone.now() - timedelta(days=90)

        mentions = (
            party.mentions.select_related('portal', 'figure')
            .filter(article_date__gte=since)
            .order_by('-article_date')
        )

        figures = party.figures.filter(is_active=True).annotate(
            mention_count=Count('mentions', filter=Q(mentions__article_date__gte=since))
        ).order_by('-mention_count')

        ctx.update({
            'mentions': mentions[:30],
            'total_mentions': mentions.count(),
            'avg_sentiment': mentions.aggregate(avg=Avg('sentiment_score'))['avg'],
            'figures': figures,
            'since_days': 90,
        })
        return ctx


class MentionListView(ListView):
    model = PoliticalMention
    template_name = 'politics/mention_list.html'
    context_object_name = 'mentions'
    paginate_by = 30

    def get_queryset(self):
        qs = (
            PoliticalMention.objects.select_related('figure', 'party', 'portal')
            .order_by('-article_date')
        )
        entity = self.request.GET.get('entity', '')
        sentiment = self.request.GET.get('sentiment', '')
        portal_id = self.request.GET.get('portal', '')

        if entity:
            qs = qs.filter(portal__entity=entity)
        if sentiment in ('positive', 'negative', 'neutral'):
            qs = qs.filter(sentiment_label=sentiment)
        if portal_id:
            qs = qs.filter(portal_id=portal_id)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['portals'] = MediaPortal.objects.filter(is_active=True).order_by('name')
        ctx['selected_entity'] = self.request.GET.get('entity', '')
        ctx['selected_sentiment'] = self.request.GET.get('sentiment', '')
        ctx['selected_portal'] = self.request.GET.get('portal', '')
        return ctx
