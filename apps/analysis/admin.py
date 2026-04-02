from django.contrib import admin
from .models import AnalysisCategory, AnalysisReport, DataPoint


@admin.register(AnalysisCategory)
class AnalysisCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'sector', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class DataPointInline(admin.StackedInline):
    model = DataPoint
    extra = 1
    fields = ['chart_title', 'chart_type', 'labels_json', 'datasets_json', 'sort_order', 'caption', 'source']


@admin.register(AnalysisReport)
class AnalysisReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'is_featured', 'views_count', 'published_at']
    list_filter = ['status', 'category', 'is_featured']
    list_editable = ['status', 'is_featured']
    search_fields = ['title', 'executive_sum']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    date_hierarchy = 'published_at'
    filter_horizontal = ['tags']
    inlines = [DataPointInline]
