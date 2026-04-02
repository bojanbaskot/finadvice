from django.contrib import admin
from .models import Bank, InterestRateOffer, ScrapeLog, CurrencyRate, SavedCalculation


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name', 'country', 'is_active']
    list_filter = ['country', 'is_active']
    list_editable = ['is_active']


@admin.register(InterestRateOffer)
class InterestRateOfferAdmin(admin.ModelAdmin):
    list_display = ['bank', 'loan_type', 'rate', 'ert', 'rate_type', 'currency', 'is_active', 'scraped_at']
    list_filter = ['bank__country', 'loan_type', 'rate_type', 'is_active', 'currency']
    list_editable = ['is_active']
    search_fields = ['bank__name']
    readonly_fields = ['scraped_at']


@admin.register(ScrapeLog)
class ScrapeLogAdmin(admin.ModelAdmin):
    list_display = ['bank', 'status', 'records_found', 'records_updated', 'created_at']
    list_filter = ['status', 'bank']
    readonly_fields = ['bank', 'status', 'records_found', 'records_updated', 'error_message', 'created_at']

    def has_add_permission(self, request):
        return False


@admin.register(CurrencyRate)
class CurrencyRateAdmin(admin.ModelAdmin):
    list_display = ['base_currency', 'target_currency', 'rate', 'fetched_at']
    readonly_fields = ['fetched_at']


@admin.register(SavedCalculation)
class SavedCalculationAdmin(admin.ModelAdmin):
    list_display = ['user', 'calc_type', 'label', 'created_at']
    list_filter = ['calc_type']
    readonly_fields = ['user', 'calc_type', 'inputs_json', 'results_json', 'created_at']
