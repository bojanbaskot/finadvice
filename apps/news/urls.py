from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.NewsListView.as_view(), name='news-list'),
    path('tag/<slug:slug>/', views.NewsTagView.as_view(), name='news-tag'),
    path('kategorija/<slug:slug>/', views.NewsCategoryView.as_view(), name='news-category'),
    path('nekretnine/', views.PropertyListView.as_view(), name='property-list'),
    path('nekretnine/<slug:slug>/', views.PropertyDetailView.as_view(), name='property-detail'),
    path('<slug:slug>/', views.NewsDetailView.as_view(), name='news-detail'),
]
