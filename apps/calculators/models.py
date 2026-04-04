from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import TimeStampedModel

User = get_user_model()


class Bank(TimeStampedModel):
    COUNTRY_CHOICES = [('BA', 'Bosnia & Herzegovina'), ('RS', 'Serbia')]

    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='banks/', blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['country', 'name']

    def __str__(self):
        return f'{self.name} ({self.country})'


class InterestRateOffer(TimeStampedModel):
    LOAN_TYPE_CHOICES = [
        ('stambeni', 'Stambeni kredit'),
        ('gotovinski', 'Gotovinski kredit'),
        ('auto', 'Auto kredit'),
        ('penzionerski', 'Penzionerski kredit'),
        ('potrosacki', 'Potrošački kredit'),
        ('refinansiranje', 'Refinansiranje'),
        ('poslovni', 'Poslovni kredit'),
    ]
    RATE_TYPE_CHOICES = [('fixed', 'Fixed'), ('variable', 'Variable'), ('mixed', 'Fixed+Variable')]

    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='rate_offers')
    loan_type = models.CharField(max_length=20, choices=LOAN_TYPE_CHOICES)
    rate = models.DecimalField(max_digits=5, decimal_places=2, help_text='Annual interest rate %')
    rate_type = models.CharField(max_length=10, choices=RATE_TYPE_CHOICES, default='fixed')
    ert = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                              help_text='Effective rate (ERT/EKS) %')
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    min_term_months = models.PositiveSmallIntegerField(null=True, blank=True)
    max_term_months = models.PositiveSmallIntegerField(null=True, blank=True)
    currency = models.CharField(max_length=3, default='BAM',
                                choices=[('BAM', 'BAM'), ('EUR', 'EUR'), ('RSD', 'RSD')])
    notes = models.TextField(blank=True)
    source_url = models.URLField(blank=True)
    scraped_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['loan_type', 'rate']

    def __str__(self):
        return f'{self.bank.name} - {self.get_loan_type_display()} {self.rate}%'


class ScrapeLog(TimeStampedModel):
    STATUS_CHOICES = [('success', 'Success'), ('partial', 'Partial'), ('failed', 'Failed')]

    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='scrape_logs')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    records_found = models.PositiveSmallIntegerField(default=0)
    records_updated = models.PositiveSmallIntegerField(default=0)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.bank.name} scrape - {self.status}'


class CurrencyRate(models.Model):
    base_currency = models.CharField(max_length=3)
    target_currency = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=18, decimal_places=6)
    fetched_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('base_currency', 'target_currency')
        ordering = ['base_currency', 'target_currency']

    def __str__(self):
        return f'{self.base_currency}/{self.target_currency} = {self.rate}'


class SavedCalculation(TimeStampedModel):
    CALC_TYPE_CHOICES = [
        ('loan', 'Loan Calculator'),
        ('mortgage', 'Mortgage Calculator'),
        ('investment', 'Investment Return'),
        ('savings', 'Savings Goal'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_calculations')
    calc_type = models.CharField(max_length=20, choices=CALC_TYPE_CHOICES)
    label = models.CharField(max_length=200, blank=True)
    inputs_json = models.JSONField()
    results_json = models.JSONField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_calc_type_display()} - {self.label}'
