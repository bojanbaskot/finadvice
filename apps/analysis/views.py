from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import F
from .models import AnalysisReport, AnalysisCategory


class AnalysisListView(ListView):
    model = AnalysisReport
    template_name = 'analysis/analysis_list.html'
    context_object_name = 'reports'
    paginate_by = 9

    def get_queryset(self):
        return AnalysisReport.published.all().select_related('category', 'author')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = AnalysisCategory.objects.all()
        ctx['sectors'] = AnalysisCategory.SECTOR_CHOICES
        ctx['featured'] = AnalysisReport.published.featured()[:3]
        return ctx


class AnalysisDetailView(DetailView):
    model = AnalysisReport
    template_name = 'analysis/analysis_detail.html'
    context_object_name = 'report'

    def get_queryset(self):
        return AnalysisReport.published.all()

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        AnalysisReport.objects.filter(pk=obj.pk).update(views_count=F('views_count') + 1)
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        report = self.object
        ctx['data_points'] = report.data_points.all()
        ctx['related'] = AnalysisReport.published.filter(
            category=report.category
        ).exclude(pk=report.pk)[:4]
        return ctx


class AnalysisCategoryView(ListView):
    template_name = 'analysis/analysis_list.html'
    context_object_name = 'reports'
    paginate_by = 9

    def get_queryset(self):
        self.category = get_object_or_404(AnalysisCategory, slug=self.kwargs['slug'])
        return AnalysisReport.published.filter(category=self.category).select_related('category')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['current_category'] = self.category
        ctx['categories'] = AnalysisCategory.objects.all()
        ctx['sectors'] = AnalysisCategory.SECTOR_CHOICES
        return ctx


class AnalysisSectorView(ListView):
    template_name = 'analysis/analysis_list.html'
    context_object_name = 'reports'
    paginate_by = 9

    def get_queryset(self):
        self.sector = self.kwargs['sector']
        return AnalysisReport.published.by_sector(self.sector).select_related('category')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['current_sector'] = self.sector
        ctx['categories'] = AnalysisCategory.objects.all()
        ctx['sectors'] = AnalysisCategory.SECTOR_CHOICES
        return ctx
