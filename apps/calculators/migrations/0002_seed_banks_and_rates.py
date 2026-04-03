from django.db import migrations
from django.utils import timezone


BANKS = [
    {'name': 'UniCredit Bank BH', 'short_name': 'unicredit-bh', 'country': 'BA', 'website': 'https://www.unicreditbank.ba'},
    {'name': 'Raiffeisen Bank BH', 'short_name': 'raiffeisen-bh', 'country': 'BA', 'website': 'https://www.raiffeisenbank.ba'},
    {'name': 'NLB Banka BH', 'short_name': 'nlb-bh', 'country': 'BA', 'website': 'https://www.nlb.ba'},
    {'name': 'Sparkasse Bank BH', 'short_name': 'sparkasse-bh', 'country': 'BA', 'website': 'https://www.sparkasse.ba'},
    {'name': 'Raiffeisen Bank Srbija', 'short_name': 'raiffeisen-rs', 'country': 'RS', 'website': 'https://www.raiffeisenbank.rs'},
    {'name': 'OTP Banka Srbija', 'short_name': 'otp-rs', 'country': 'RS', 'website': 'https://www.otpbanka.rs'},
]

SAMPLE_RATES = [
    # (bank_short_name, loan_type, rate, ert, currency)
    ('unicredit-bh', 'stambeni', 3.99, 4.21, 'BAM'),
    ('unicredit-bh', 'gotovinski', 6.99, 7.45, 'BAM'),
    ('unicredit-bh', 'auto', 5.49, 5.89, 'BAM'),
    ('raiffeisen-bh', 'stambeni', 3.75, 3.98, 'BAM'),
    ('raiffeisen-bh', 'gotovinski', 7.25, 7.82, 'BAM'),
    ('raiffeisen-bh', 'auto', 5.25, 5.71, 'BAM'),
    ('nlb-bh', 'stambeni', 4.10, 4.35, 'BAM'),
    ('nlb-bh', 'gotovinski', 6.75, 7.21, 'BAM'),
    ('nlb-bh', 'refinansiranje', 6.50, 6.95, 'BAM'),
    ('sparkasse-bh', 'stambeni', 3.85, 4.10, 'BAM'),
    ('sparkasse-bh', 'gotovinski', 7.10, 7.65, 'BAM'),
    ('raiffeisen-rs', 'stambeni', 4.50, 4.85, 'RSD'),
    ('raiffeisen-rs', 'gotovinski', 8.99, 9.75, 'RSD'),
    ('raiffeisen-rs', 'auto', 6.99, 7.45, 'RSD'),
    ('otp-rs', 'stambeni', 4.25, 4.60, 'RSD'),
    ('otp-rs', 'gotovinski', 8.50, 9.25, 'RSD'),
]


def seed_banks_and_rates(apps, schema_editor):
    Bank = apps.get_model('calculators', 'Bank')
    InterestRateOffer = apps.get_model('calculators', 'InterestRateOffer')

    bank_map = {}
    for b in BANKS:
        bank, _ = Bank.objects.get_or_create(
            short_name=b['short_name'],
            defaults={
                'name': b['name'],
                'country': b['country'],
                'website': b['website'],
                'is_active': True,
            }
        )
        bank_map[b['short_name']] = bank

    now = timezone.now()
    for short_name, loan_type, rate, ert, currency in SAMPLE_RATES:
        bank = bank_map.get(short_name)
        if bank:
            InterestRateOffer.objects.get_or_create(
                bank=bank,
                loan_type=loan_type,
                defaults={
                    'rate': rate,
                    'ert': ert,
                    'currency': currency,
                    'is_active': True,
                    'scraped_at': now,
                }
            )


def remove_seed_data(apps, schema_editor):
    Bank = apps.get_model('calculators', 'Bank')
    Bank.objects.filter(short_name__in=[b['short_name'] for b in BANKS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('calculators', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_banks_and_rates, remove_seed_data),
    ]
