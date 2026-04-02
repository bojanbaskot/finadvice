from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import F
from .models import NewsArticle, NewsCategory, NewsTag, Property, PropertyCategory


class NewsListView(ListView):
    model = NewsArticle
    template_name = 'news/news_list.html'
    context_object_name = 'articles'
    paginate_by = 12

    def get_queryset(self):
        return NewsArticle.published.all().select_related('category', 'author')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = NewsCategory.objects.all()
        ctx['featured'] = NewsArticle.published.featured()[:3]
        return ctx


class NewsDetailView(DetailView):
    model = NewsArticle
    template_name = 'news/news_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        return NewsArticle.published.all()

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        NewsArticle.objects.filter(pk=obj.pk).update(views_count=F('views_count') + 1)
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        article = self.object
        ctx['related'] = NewsArticle.published.filter(
            category=article.category
        ).exclude(pk=article.pk)[:4]
        return ctx


class NewsCategoryView(ListView):
    template_name = 'news/news_list.html'
    context_object_name = 'articles'
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(NewsCategory, slug=self.kwargs['slug'])
        return NewsArticle.published.filter(category=self.category).select_related('category')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['current_category'] = self.category
        ctx['categories'] = NewsCategory.objects.all()
        return ctx


class NewsTagView(ListView):
    template_name = 'news/news_list.html'
    context_object_name = 'articles'
    paginate_by = 12

    def get_queryset(self):
        self.tag = get_object_or_404(NewsTag, slug=self.kwargs['slug'])
        return NewsArticle.published.filter(tags=self.tag).select_related('category')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['current_tag'] = self.tag
        ctx['categories'] = NewsCategory.objects.all()
        return ctx


class PropertyListView(ListView):
    model = Property
    template_name = 'news/property_list.html'
    context_object_name = 'properties'
    paginate_by = 12

    def get_queryset(self):
        qs = Property.active.all().prefetch_related('images').select_related('category')
        listing_type = self.request.GET.get('tip')
        country = self.request.GET.get('zemlja')
        city = self.request.GET.get('grad')
        min_price = self.request.GET.get('min_cijena')
        max_price = self.request.GET.get('max_cijena')
        if listing_type:
            qs = qs.filter(listing_type=listing_type)
        if country:
            qs = qs.filter(country=country)
        if city:
            qs = qs.filter(city__icontains=city)
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = PropertyCategory.objects.all()
        ctx['countries'] = Property.COUNTRY_CHOICES
        return ctx


class PropertyDetailView(DetailView):
    model = Property
    template_name = 'news/property_detail.html'
    context_object_name = 'property'

    def get_queryset(self):
        return Property.active.all()

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        Property.objects.filter(pk=obj.pk).update(views_count=F('views_count') + 1)
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        prop = self.object
        ctx['related'] = Property.active.filter(city=prop.city).exclude(pk=prop.pk)[:4]
        ctx['images'] = prop.images.all()
        ctx['features'] = prop.features.all()
        return ctx
