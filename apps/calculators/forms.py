from django import forms


class LoanCalculatorForm(forms.Form):
    principal = forms.DecimalField(
        label='Iznos kredita (BAM)', min_value=1000, max_value=10_000_000, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '50000'})
    )
    annual_rate = forms.DecimalField(
        label='Godišnja kamatna stopa (%)', min_value=0, max_value=50, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '4.5', 'step': '0.01'})
    )
    term_months = forms.IntegerField(
        label='Rok otplate (mjeseci)', min_value=1, max_value=480,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '120'})
    )


class MortgageCalculatorForm(forms.Form):
    property_value = forms.DecimalField(
        label='Vrijednost nekretnine (BAM)', min_value=1000, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '200000'})
    )
    down_payment = forms.DecimalField(
        label='Učešće / avans (BAM)', min_value=0, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '40000'})
    )
    annual_rate = forms.DecimalField(
        label='Godišnja kamatna stopa (%)', min_value=0, max_value=50, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '3.9', 'step': '0.01'})
    )
    term_months = forms.IntegerField(
        label='Rok otplate (mjeseci)', min_value=12, max_value=360,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '240'})
    )


class InvestmentCalculatorForm(forms.Form):
    initial = forms.DecimalField(
        label='Početna investicija (BAM)', min_value=0, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '10000'})
    )
    monthly_contribution = forms.DecimalField(
        label='Mjesečni ulog (BAM)', min_value=0, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '200'})
    )
    annual_rate = forms.DecimalField(
        label='Godišnji prinos (%)', min_value=0, max_value=100, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '7', 'step': '0.1'})
    )
    years = forms.IntegerField(
        label='Broj godina', min_value=1, max_value=50,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '20'})
    )


class SavingsCalculatorForm(forms.Form):
    target_amount = forms.DecimalField(
        label='Ciljani iznos štednje (BAM)', min_value=1, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '50000'})
    )
    current_savings = forms.DecimalField(
        label='Trenutna uštedjevina (BAM)', min_value=0, decimal_places=2, initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '5000'})
    )
    annual_rate = forms.DecimalField(
        label='Godišnja kamatna stopa (%)', min_value=0, max_value=50, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '3', 'step': '0.01'})
    )
    monthly_contribution = forms.DecimalField(
        label='Mjesečni ulog (BAM)', min_value=1, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '500'})
    )


class LoanComparisonForm(forms.Form):
    principal = forms.DecimalField(
        label='Iznos kredita (BAM)', min_value=1000, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '50000'})
    )
    term_months = forms.IntegerField(
        label='Rok otplate (mjeseci)', min_value=1, max_value=480,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '120'})
    )
    loan_type = forms.ChoiceField(
        label='Vrsta kredita',
        choices=[
            ('stambeni', 'Stambeni kredit'),
            ('gotovinski', 'Gotovinski kredit'),
            ('auto', 'Auto kredit'),
            ('penzionerski', 'Penzionerski kredit'),
            ('refinansiranje', 'Refinansiranje'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class DepositCalculatorForm(forms.Form):
    COMPOUND_CHOICES = [
        ('monthly', 'Mjesečno (složena)'),
        ('quarterly', 'Kvartalno'),
        ('annual', 'Godišnje'),
        ('at_maturity', 'Po isteku roka'),
    ]
    principal = forms.DecimalField(
        label='Iznos depozita (BAM)', min_value=100, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '10000'})
    )
    annual_rate = forms.DecimalField(
        label='Godišnja kamatna stopa (%)', min_value=0.01, max_value=20, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '3.5', 'step': '0.01'})
    )
    term_months = forms.IntegerField(
        label='Rok oročenja (mjeseci)', min_value=1, max_value=120,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '12'})
    )
    compound = forms.ChoiceField(
        label='Način obračuna kamate', choices=COMPOUND_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class CurrencyConverterForm(forms.Form):
    CURRENCIES = [
        ('BAM', 'BAM — Konvertibilna marka'),
        ('EUR', 'EUR — Euro'),
        ('USD', 'USD — Američki dolar'),
        ('RSD', 'RSD — Srpski dinar'),
        ('CHF', 'CHF — Švicarski franak'),
    ]
    amount = forms.DecimalField(
        label='Iznos', min_value=0.01, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'placeholder': '1000'})
    )
    from_currency = forms.ChoiceField(
        label='Iz valute', choices=CURRENCIES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    to_currency = forms.ChoiceField(
        label='U valutu', choices=CURRENCIES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['to_currency'].initial = 'EUR'
