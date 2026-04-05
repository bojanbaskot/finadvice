from django.urls import path
from . import views

app_name = 'politics'

urlpatterns = [
    path('', views.PoliticsDashboardView.as_view(), name='dashboard'),
    path('pomeni/', views.MentionListView.as_view(), name='mention-list'),
    path('akter/<slug:slug>/', views.FigureDetailView.as_view(), name='figure-detail'),
    path('stranka/<slug:abbreviation>/', views.PartyDetailView.as_view(), name='party-detail'),
]
