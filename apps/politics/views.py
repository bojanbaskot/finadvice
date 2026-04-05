from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.views.generic import TemplateView, DetailView, ListView
from datetime import timedelta

from .models import (
    PoliticalFigure, PoliticalParty, MediaPortal,
    PoliticalMention, MentionScrapeLog,
)


class PoliticsDashboardView(TemplateView):
    template_name = 'politics/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        since = timezone.now() - timedelta(days=30)

        # Top figures by mention count (last 30 days)
        top_figures = (
            PoliticalFigure.objects.filter(is_active=True)
            .annotate(
                mention_count=Count('mentions', filter=Q(mentions__article_date__gte=since)),
                avg_sentiment=Avg('mentions__sentiment_score', filter=Q(mentions__article_date__gte=since)),
            )
            .filter(mention_count__gt=0)
            .order_by('-mention_count')[:10]
        )

        # Top parties by mention count
        top_parties = (
            PoliticalParty.objects.filter(is_active=True)
            .annotate(
                mention_count=Count('mentions', filter=Q(mentions__article_date__gte=since)),
                avg_sentiment=Avg('mentions__sentiment_score', filter=Q(mentions__article_date__gte=since)),
            )
            .filter(mention_count__gt=0)
            .order_by('-mention_count')[:8]
        )

        # Recent mentions
        recent_mentions = (
            PoliticalMention.objects.select_related('figure', 'party', 'portal')
            .filter(article_date__gte=since)
            .order_by('-article_date')[:20]
        )

        # Sentiment totals
        total = PoliticalMention.objects.filter(article_date__gte=since).count()
        pos = PoliticalMention.objects.filter(article_date__gte=since, sentiment_label='positive').count()
        neg = PoliticalMention.objects.filter(article_date__gte=since, sentiment_label='negative').count()
        neu = total - pos - neg

        # Entity split: RS vs FBiH portals
        rs_mentions = PoliticalMention.objects.filter(
            article_date__gte=since, portal__entity='RS'
        ).count()
        fbih_mentions = PoliticalMention.objects.filter(
            article_date__gte=since, portal__entity='FBiH'
        ).count()

        ctx.update({
            'top_figures': top_figures,
            'top_parties': top_parties,
            'recent_mentions': recent_mentions,
            'total_mentions': total,
            'positive_count': pos,
            'negative_count': neg,
            'neutral_count': neu,
            'rs_mentions': rs_mentions,
            'fbih_mentions': fbih_mentions,
            'since_days': 30,
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
