from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.db.models import Q


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from apps.news.models import NewsArticle, Property
        from apps.elearning.models import Course
        from apps.analysis.models import AnalysisReport
        from apps.calculators.models import InterestRateOffer

        ctx['featured_news'] = NewsArticle.objects.filter(
            status='published', is_featured=True
        ).select_related('category')[:4]
        ctx['latest_news'] = NewsArticle.objects.filter(
            status='published'
        ).select_related('category')[:6]
        ctx['featured_properties'] = Property.objects.filter(
            status='active', is_featured=True
        ).prefetch_related('images')[:4]
        ctx['featured_courses'] = Course.objects.filter(
            status='published'
        ).select_related('category')[:3]
        ctx['featured_analysis'] = AnalysisReport.objects.filter(
            status__in=['published', 'premium'], is_featured=True
        ).select_related('category')[:3]
        ctx['latest_rates'] = InterestRateOffer.objects.filter(
            is_active=True
        ).select_related('bank').order_by('rate')[:5]
        return ctx


class AboutView(TemplateView):
    template_name = 'core/about.html'


class ContactView(TemplateView):
    template_name = 'core/contact.html'


class SearchView(View):
    template_name = 'core/search_results.html'

    def get(self, request):
        query = request.GET.get('q', '').strip()
        results = {'news': [], 'properties': [], 'courses': [], 'analysis': []}
        if query and len(query) >= 3:
            from apps.news.models import NewsArticle, Property
            from apps.elearning.models import Course
            from apps.analysis.models import AnalysisReport

            results['news'] = NewsArticle.objects.filter(
                status='published'
            ).filter(Q(title__icontains=query) | Q(excerpt__icontains=query))[:10]
            results['properties'] = Property.objects.filter(
                status='active'
            ).filter(Q(title__icontains=query) | Q(city__icontains=query))[:10]
            results['courses'] = Course.objects.filter(
                status='published'
            ).filter(Q(title__icontains=query) | Q(subtitle__icontains=query))[:10]
            results['analysis'] = AnalysisReport.objects.filter(
                status__in=['published', 'premium']
            ).filter(Q(title__icontains=query) | Q(executive_sum__icontains=query))[:10]

        return render(request, self.template_name, {'query': query, 'results': results})
