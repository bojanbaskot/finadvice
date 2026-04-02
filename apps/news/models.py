from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model
from ckeditor_uploader.fields import RichTextUploadingField
from apps.core.models import TimeStampedModel

User = get_user_model()


class NewsCategory(TimeStampedModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = 'News Category'
        verbose_name_plural = 'News Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('news:news-category', kwargs={'slug': self.slug})


class NewsTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('news:news-tag', kwargs={'slug': self.slug})


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published')

    def featured(self):
        return self.get_queryset().filter(is_featured=True)


class NewsArticle(TimeStampedModel):
    STATUS_CHOICES = [('draft', 'Draft'), ('published', 'Published'), ('archived', 'Archived')]

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    excerpt = models.TextField(max_length=500)
    body = RichTextUploadingField()
    cover_image = models.ImageField(upload_to='news/%Y/%m/', blank=True)
    category = models.ForeignKey(NewsCategory, on_delete=models.PROTECT, related_name='articles')
    tags = models.ManyToManyField(NewsTag, blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    source_url = models.URLField(blank=True)
    source_name = models.CharField(max_length=100, blank=True)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news:news-detail', kwargs={'slug': self.slug})

    def publish(self):
        self.status = 'published'
        self.published_at = timezone.now()
        self.save()


class PropertyCategory(TimeStampedModel):
    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'Apartment'), ('house', 'House'), ('land', 'Land'),
        ('commercial', 'Commercial'), ('office', 'Office'),
    ]
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    icon = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = 'Property Category'
        verbose_name_plural = 'Property Categories'

    def __str__(self):
        return self.name


class ActivePropertyManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='active')

    def featured(self):
        return self.get_queryset().filter(is_featured=True)


class Property(TimeStampedModel):
    LISTING_TYPE_CHOICES = [('sale', 'For Sale'), ('rent', 'For Rent')]
    COUNTRY_CHOICES = [('BA', 'Bosnia & Herzegovina'), ('RS', 'Serbia'), ('ME', 'Montenegro'), ('HR', 'Croatia')]
    STATUS_CHOICES = [('active', 'Active'), ('sold', 'Sold'), ('rented', 'Rented'), ('inactive', 'Inactive')]
    CURRENCY_CHOICES = [('EUR', 'EUR'), ('BAM', 'BAM'), ('RSD', 'RSD')]

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    description = RichTextUploadingField()
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPE_CHOICES)
    category = models.ForeignKey(PropertyCategory, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='EUR')
    price_per_sqm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    area_sqm = models.DecimalField(max_digits=10, decimal_places=2)
    rooms = models.PositiveSmallIntegerField(null=True, blank=True)
    floor = models.SmallIntegerField(null=True, blank=True)
    total_floors = models.SmallIntegerField(null=True, blank=True)
    year_built = models.PositiveSmallIntegerField(null=True, blank=True)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    city = models.CharField(max_length=100)
    municipality = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_featured = models.BooleanField(default=False)
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    contact_email = models.EmailField(blank=True)
    views_count = models.PositiveIntegerField(default=0)

    objects = models.Manager()
    active = ActivePropertyManager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news:property-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if self.area_sqm and self.price:
            self.price_per_sqm = self.price / self.area_sqm
        super().save(*args, **kwargs)

    @property
    def cover_image(self):
        img = self.images.filter(is_cover=True).first()
        if not img:
            img = self.images.first()
        return img


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='realestate/%Y/%m/')
    caption = models.CharField(max_length=200, blank=True)
    is_cover = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'Image for {self.property.title}'


class PropertyFeature(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)
    properties = models.ManyToManyField(Property, related_name='features', blank=True)

    def __str__(self):
        return self.name
