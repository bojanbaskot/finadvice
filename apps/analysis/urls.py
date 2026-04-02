from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    path('', views.AnalysisListView.as_view(), name='analysis-list'),
    path('kategorija/<slug:slug>/', views.AnalysisCategoryView.as_view(), name='analysis-category'),
    path('sektor/<str:sector>/', views.AnalysisSectorView.as_view(), name='analysis-sector'),
    path('<slug:slug>/', views.AnalysisDetailView.as_view(), name='analysis-detail'),
]
