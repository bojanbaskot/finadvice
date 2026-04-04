from django.urls import path
from . import views

app_name = 'calculators'

urlpatterns = [
    path('', views.CalculatorIndexView.as_view(), name='index'),
    path('kredit/', views.LoanCalculatorView.as_view(), name='loan'),
    path('hipoteka/', views.MortgageCalculatorView.as_view(), name='mortgage'),
    path('investicija/', views.InvestmentCalculatorView.as_view(), name='investment'),
    path('stednja/', views.SavingsCalculatorView.as_view(), name='savings'),
    path('poredjenje-kredita/', views.LoanComparisonView.as_view(), name='comparison'),
    path('kamatne-stope/', views.InterestRatesView.as_view(), name='interest-rates'),
    path('depozit/', views.DepositCalculatorView.as_view(), name='deposit'),
    path('valute/', views.CurrencyConverterView.as_view(), name='currency'),
]
