from django.contrib import admin
from .models import (
    PoliticalParty, PoliticalFigure, MediaPortal,
    PoliticalMention, MentionScrapeLog,
)


@admin.register(PoliticalParty)
class PoliticalPartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation', 'entity', 'is_active')
    list_filter = ('entity', 'is_active')
    search_fields = ('name', 'abbreviation')


@admin.register(PoliticalFigure)
class PoliticalFigureAdmin(admin.ModelAdmin):
    list_display = ('name', 'party', 'entity', 'current_position', 'is_active')
    list_filter = ('entity', 'is_active', 'party')
    search_fields = ('name', 'name_variations', 'current_position')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(MediaPortal)
class MediaPortalAdmin(admin.ModelAdmin):
    list_display = ('name', 'entity', 'portal_type', 'has_rss', 'is_active', 'last_scraped', 'articles_collected')
    list_filter = ('entity', 'portal_type', 'is_active')
    search_fields = ('name', 'url', 'rss_url')
    list_editable = ('is_active',)
    actions = ['activate', 'deactivate']

    @admin.display(boolean=True, description='RSS')
    def has_rss(self, obj):
        return bool(obj.rss_url)

    @admin.action(description='Aktiviraj odabrane portale')
    def activate(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Deaktiviraj odabrane portale')
    def deactivate(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(PoliticalMention)
class PoliticalMentionAdmin(admin.ModelAdmin):
    list_display = ('article_title_short', 'figure', 'party', 'portal', 'article_date', 'sentiment_label', 'sentiment_score')
    list_filter = ('sentiment_label', 'portal__entity', 'portal')
    search_fields = ('article_title', 'article_url', 'excerpt')
    date_hierarchy = 'article_date'
    readonly_fields = ('article_url', 'sentiment_score', 'sentiment_label', 'excerpt')

    def article_title_short(self, obj):
        return obj.article_title[:70]
    article_title_short.short_description = 'Naslov'


@admin.register(MentionScrapeLog)
class MentionScrapeLogAdmin(admin.ModelAdmin):
    list_display = ('portal', 'status', 'articles_checked', 'mentions_found', 'created_at')
    list_filter = ('status', 'portal')
    readonly_fields = ('portal', 'status', 'articles_checked', 'mentions_found', 'error_message', 'created_at')
