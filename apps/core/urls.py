from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('pretraga/', views.SearchView.as_view(), name='search'),
    path('o-nama/', views.AboutView.as_view(), name='about'),
    path('kontakt/', views.ContactView.as_view(), name='contact'),
]
