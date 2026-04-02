from django.contrib import admin
from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General', {'fields': ('site_name', 'tagline', 'footer_text')}),
        ('Contact', {'fields': ('contact_email', 'phone', 'address')}),
        ('Social', {'fields': ('facebook_url', 'linkedin_url')}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
