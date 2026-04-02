from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model
from ckeditor_uploader.fields import RichTextUploadingField
from apps.core.models import TimeStampedModel

User = get_user_model()


class AnalysisCategory(TimeStampedModel):
    SECTOR_CHOICES = [
        ('banking', 'Banking & Finance'),
        ('realestate', 'Real Estate Market'),
        ('macro', 'Macroeconomics'),
        ('investment', 'Investment'),
        ('crypto', 'Crypto & Digital Assets'),
        ('regional', 'Western Balkans Region'),
        ('eu', 'EU Integration'),
    ]
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    sector = models.CharField(max_length=20, choices=SECTOR_CHOICES)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = 'Analysis Category'
        verbose_name_plural = 'Analysis Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('analysis:analysis-category', kwargs={'slug': self.slug})


class PublishedAnalysisManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status__in=['published', 'premium'])

    def featured(self):
        return self.get_queryset().filter(is_featured=True)

    def by_sector(self, sector):
        return self.get_queryset().filter(category__sector=sector)


class AnalysisReport(TimeStampedModel):
    STATUS_CHOICES = [('draft', 'Draft'), ('published', 'Published'), ('premium', 'Premium')]

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    subtitle = models.CharField(max_length=500, blank=True)
    executive_sum = models.TextField(help_text='Executive summary shown in listing cards')
    body = RichTextUploadingField()
    cover_image = models.ImageField(upload_to='analysis/%Y/%m/', blank=True)
    category = models.ForeignKey(AnalysisCategory, on_delete=models.PROTECT, related_name='reports')
    tags = models.ManyToManyField('news.NewsTag', blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    pdf_export = models.FileField(upload_to='analysis/pdfs/', blank=True)
    reading_time_min = models.PositiveSmallIntegerField(default=5)

    objects = models.Manager()
    published = PublishedAnalysisManager()

    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('analysis:analysis-detail', kwargs={'slug': self.slug})

    def publish(self):
        self.status = 'published'
        self.published_at = timezone.now()
        self.save()


class DataPoint(models.Model):
    CHART_TYPE_CHOICES = [
        ('line', 'Line'), ('bar', 'Bar'), ('pie', 'Pie'),
        ('doughnut', 'Doughnut'), ('area', 'Area'),
    ]
    report = models.ForeignKey(AnalysisReport, on_delete=models.CASCADE, related_name='data_points')
    chart_title = models.CharField(max_length=200)
    chart_type = models.CharField(max_length=10, choices=CHART_TYPE_CHOICES, default='line')
    labels_json = models.JSONField(help_text='List of X-axis labels')
    datasets_json = models.JSONField(help_text='Chart.js datasets array')
    sort_order = models.PositiveSmallIntegerField(default=0)
    caption = models.CharField(max_length=300, blank=True)
    source = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return f'{self.report.title} - {self.chart_title}'
