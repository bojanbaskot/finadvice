from django.db import models
from apps.core.models import TimeStampedModel


ENTITY_CHOICES = [
    ('BiH', 'Bosna i Hercegovina'),
    ('FBiH', 'Federacija BiH'),
    ('RS', 'Republika Srpska'),
    ('BD', 'Brčko distrikt'),
]

PORTAL_ENTITY_CHOICES = [
    ('FBiH', 'Federacija BiH'),
    ('RS', 'Republika Srpska'),
    ('BD', 'Brčko distrikt'),
    ('national', 'Cijela BiH'),
]


class PoliticalParty(TimeStampedModel):
    name = models.CharField(max_length=300)
    abbreviation = models.CharField(max_length=30, blank=True)
    entity = models.CharField(max_length=10, choices=ENTITY_CHOICES, default='BiH')
    ideology = models.CharField(max_length=200, blank=True)
    logo = models.ImageField(upload_to='politics/parties/', blank=True)
    cik_id = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Politicka stranka'
        verbose_name_plural = 'Politicke stranke'
        ordering = ['name']

    def __str__(self):
        return self.abbreviation or self.name


class PoliticalFigure(TimeStampedModel):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    party = models.ForeignKey(
        PoliticalParty, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='figures'
    )
    entity = models.CharField(max_length=10, choices=ENTITY_CHOICES, default='BiH')
    current_position = models.CharField(max_length=300, blank=True)
    photo = models.ImageField(upload_to='politics/figures/', blank=True)
    name_variations = models.TextField(
        blank=True,
        help_text='Varijante imena odvojene zarezom (za pretragu portalima)'
    )
    cik_id = models.CharField(max_length=50, blank=True)
    was_in_previous_cycle = models.BooleanField(default=False)
    running_for = models.CharField(max_length=300, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Politicki akter'
        verbose_name_plural = 'Politicki akteri'
        ordering = ['name']

    def __str__(self):
        party_str = f' ({self.party.abbreviation})' if self.party else ''
        return f'{self.name}{party_str}'

    def get_name_list(self):
        base = [self.name]
        if self.name_variations:
            extras = [v.strip() for v in self.name_variations.split(',') if v.strip()]
            base.extend(extras)
        return list(set(base))


class MediaPortal(TimeStampedModel):
    PORTAL_TYPE_CHOICES = [
        ('online', 'Online portal'),
        ('tv', 'Televizija'),
        ('radio', 'Radio'),
        ('print', 'Stampa'),
        ('agency', 'Novinska agencija'),
    ]

    name = models.CharField(max_length=200)
    url = models.URLField()
    rss_url = models.URLField(blank=True)
    entity = models.CharField(max_length=10, choices=PORTAL_ENTITY_CHOICES, default='national')
    portal_type = models.CharField(max_length=10, choices=PORTAL_TYPE_CHOICES, default='online')
    rak_id = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    last_scraped = models.DateTimeField(null=True, blank=True)
    articles_collected = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Medijski portal'
        verbose_name_plural = 'Medijski portali'
        ordering = ['entity', 'name']

    def __str__(self):
        return f'{self.name} ({self.get_entity_display()})'


class PoliticalMention(TimeStampedModel):
    SENTIMENT_CHOICES = [
        ('positive', 'Pozitivno'),
        ('negative', 'Negativno'),
        ('neutral', 'Neutralno'),
    ]

    figure = models.ForeignKey(
        PoliticalFigure, on_delete=models.CASCADE,
        related_name='mentions', null=True, blank=True
    )
    party = models.ForeignKey(
        PoliticalParty, on_delete=models.CASCADE,
        related_name='mentions', null=True, blank=True
    )
    portal = models.ForeignKey(
        MediaPortal, on_delete=models.CASCADE, related_name='mentions'
    )
    article_title = models.CharField(max_length=500)
    article_url = models.URLField(max_length=800, unique=True)
    article_date = models.DateTimeField()
    excerpt = models.TextField(blank=True)
    sentiment_score = models.FloatField(null=True, blank=True)
    sentiment_label = models.CharField(max_length=10, choices=SENTIMENT_CHOICES, default='neutral')
    mention_count = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = 'Pomen'
        verbose_name_plural = 'Pomeni'
        ordering = ['-article_date']
        indexes = [
            models.Index(fields=['figure', 'article_date']),
            models.Index(fields=['portal', 'article_date']),
            models.Index(fields=['sentiment_label']),
        ]

    def __str__(self):
        name = self.figure.name if self.figure else (str(self.party) if self.party else '?')
        return f'{name} @ {self.portal.name} ({self.article_date.date()})'


class MentionScrapeLog(TimeStampedModel):
    STATUS_CHOICES = [
        ('success', 'Uspjesno'),
        ('partial', 'Djelimicno'),
        ('failed', 'Neuspjesno'),
    ]

    portal = models.ForeignKey(MediaPortal, on_delete=models.CASCADE, related_name='scrape_logs')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    articles_checked = models.PositiveIntegerField(default=0)
    mentions_found = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.portal.name} — {self.status} ({self.created_at.date()})'
