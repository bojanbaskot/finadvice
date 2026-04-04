from django.shortcuts import render
from django.views.generic import View, TemplateView
from .calculators import (
    calculate_loan_annuity, calculate_mortgage,
    calculate_investment_return, calculate_savings_goal,
    calculate_deposit, convert_currency, compare_loan_offers,
)
from .forms import (
    LoanCalculatorForm, MortgageCalculatorForm,
    InvestmentCalculatorForm, SavingsCalculatorForm,
    LoanComparisonForm, DepositCalculatorForm, CurrencyConverterForm,
)
from .models import InterestRateOffer, Bank


class CalculatorIndexView(TemplateView):
    template_name = 'calculators/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['latest_rates'] = InterestRateOffer.objects.filter(
            is_active=True
        ).select_related('bank').order_by('rate')
        return ctx


class LoanCalculatorView(View):
    template_name = 'calculators/loan.html'

    def get(self, request):
        return render(request, self.template_name, {'form': LoanCalculatorForm()})

    def post(self, request):
        form = LoanCalculatorForm(request.POST)
        results = None
        if form.is_valid():
            results = calculate_loan_annuity(
                principal=form.cleaned_data['principal'],
                annual_rate_pct=form.cleaned_data['annual_rate'],
                term_months=form.cleaned_data['term_months'],
            )
        return render(request, self.template_name, {'form': form, 'results': results})


class MortgageCalculatorView(View):
    template_name = 'calculators/mortgage.html'

    def get(self, request):
        return render(request, self.template_name, {'form': MortgageCalculatorForm()})

    def post(self, request):
        form = MortgageCalculatorForm(request.POST)
        results = None
        if form.is_valid():
            results = calculate_mortgage(
                principal=form.cleaned_data['property_value'],
                annual_rate_pct=form.cleaned_data['annual_rate'],
                term_months=form.cleaned_data['term_months'],
                down_payment=form.cleaned_data['down_payment'],
                property_value=form.cleaned_data['property_value'],
            )
        return render(request, self.template_name, {'form': form, 'results': results})


class InvestmentCalculatorView(View):
    template_name = 'calculators/investment.html'

    def get(self, request):
        return render(request, self.template_name, {'form': InvestmentCalculatorForm()})

    def post(self, request):
        form = InvestmentCalculatorForm(request.POST)
        results = None
        if form.is_valid():
            results = calculate_investment_return(
                initial=form.cleaned_data['initial'],
                monthly_contribution=form.cleaned_data['monthly_contribution'],
                annual_rate_pct=form.cleaned_data['annual_rate'],
                years=form.cleaned_data['years'],
            )
        return render(request, self.template_name, {'form': form, 'results': results})


class SavingsCalculatorView(View):
    template_name = 'calculators/savings.html'

    def get(self, request):
        return render(request, self.template_name, {'form': SavingsCalculatorForm()})

    def post(self, request):
        form = SavingsCalculatorForm(request.POST)
        results = None
        if form.is_valid():
            results = calculate_savings_goal(
                target_amount=form.cleaned_data['target_amount'],
                current_savings=form.cleaned_data['current_savings'],
                annual_rate_pct=form.cleaned_data['annual_rate'],
                monthly_contribution=form.cleaned_data['monthly_contribution'],
            )
        return render(request, self.template_name, {'form': form, 'results': results})


class LoanComparisonView(View):
    template_name = 'calculators/comparison.html'

    def get(self, request):
        rates = InterestRateOffer.objects.filter(is_active=True).select_related('bank')
        return render(request, self.template_name, {'form': LoanComparisonForm(), 'rates': rates})

    def post(self, request):
        form = LoanComparisonForm(request.POST)
        results = None
        rates = InterestRateOffer.objects.filter(is_active=True).select_related('bank')
        if form.is_valid():
            loan_type = form.cleaned_data['loan_type']
            term_months = form.cleaned_data['term_months']
            principal = form.cleaned_data['principal']
            offers = [
                {'name': r.bank.name, 'rate': float(r.rate)}
                for r in rates.filter(loan_type=loan_type)
            ]
            if offers:
                results = compare_loan_offers(principal, term_months, offers)
        return render(request, self.template_name, {
            'form': form, 'results': results, 'rates': rates,
        })


class DepositCalculatorView(View):
    template_name = 'calculators/deposit.html'

    def get(self, request):
        return render(request, self.template_name, {'form': DepositCalculatorForm()})

    def post(self, request):
        form = DepositCalculatorForm(request.POST)
        results = None
        if form.is_valid():
            results = calculate_deposit(
                principal=form.cleaned_data['principal'],
                annual_rate_pct=form.cleaned_data['annual_rate'],
                term_months=form.cleaned_data['term_months'],
                compound=form.cleaned_data['compound'],
            )
        return render(request, self.template_name, {'form': form, 'results': results})


class CurrencyConverterView(View):
    template_name = 'calculators/currency.html'

    def get(self, request):
        return render(request, self.template_name, {
            'form': CurrencyConverterForm(),
            'rates_info': _get_rates_table(),
        })

    def post(self, request):
        form = CurrencyConverterForm(request.POST)
        result = None
        if form.is_valid():
            result = convert_currency(
                amount=form.cleaned_data['amount'],
                from_currency=form.cleaned_data['from_currency'],
                to_currency=form.cleaned_data['to_currency'],
            )
        return render(request, self.template_name, {
            'form': form, 'result': result,
            'rates_info': _get_rates_table(),
        })


def _get_rates_table():
    """BAM-based exchange rate table for display."""
    from .calculators import CURRENCY_RATES
    return [
        {'pair': f'{f}/{t}', 'rate': r}
        for (f, t), r in CURRENCY_RATES.items()
        if f == 'BAM'
    ]


class InterestRatesView(TemplateView):
    template_name = 'calculators/interest_rates.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        loan_type = self.request.GET.get('tip', '')
        country = self.request.GET.get('zemlja', '')
        qs = InterestRateOffer.objects.filter(is_active=True).select_related('bank')
        if loan_type:
            qs = qs.filter(loan_type=loan_type)
        if country:
            qs = qs.filter(bank__country=country)
        ctx['rates'] = qs.order_by('rate')
        ctx['loan_types'] = InterestRateOffer.LOAN_TYPE_CHOICES
        ctx['countries'] = Bank.COUNTRY_CHOICES
        ctx['banks_bh'] = Bank.objects.filter(country='BA', is_active=True)
        ctx['banks_rs'] = Bank.objects.filter(country='RS', is_active=True)
        ctx['selected_type'] = loan_type
        ctx['selected_country'] = country
        return ctx
