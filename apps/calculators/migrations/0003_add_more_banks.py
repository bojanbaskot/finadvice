from django.db import migrations
from django.utils import timezone


NEW_BANKS = [
    # Federation BiH
    {'name': 'Intesa Sanpaolo Banka BH', 'short_name': 'intesa-bh', 'country': 'BA', 'website': 'https://www.intesasanpaolobanka.ba'},
    {'name': 'Addiko Bank BH', 'short_name': 'addiko-fbih', 'country': 'BA', 'website': 'https://www.addiko-fbih.ba'},
    {'name': 'ASA Banka', 'short_name': 'asa-bh', 'country': 'BA', 'website': 'https://www.asabanka.ba'},
    {'name': 'ProCredit Bank BH', 'short_name': 'procredit-bh', 'country': 'BA', 'website': 'https://www.procreditbank.ba'},
    {'name': 'Union Banka', 'short_name': 'union-bh', 'country': 'BA', 'website': 'https://www.unionbank.ba'},
    {'name': 'Bosna Bank International', 'short_name': 'bbi-bh', 'country': 'BA', 'website': 'https://www.bbi.ba'},
    {'name': 'ZiraatBank BH', 'short_name': 'ziraat-bh', 'country': 'BA', 'website': 'https://www.ziraatbank.ba'},
    # Republic of Srpska
    {'name': 'ATOS Bank', 'short_name': 'atos-rs-ba', 'country': 'BA', 'website': 'https://www.atosbank.ba'},
    {'name': 'Nova Banka', 'short_name': 'nova-banka', 'country': 'BA', 'website': 'https://www.novabanka.com'},
    {'name': 'Addiko Bank RS', 'short_name': 'addiko-rs-ba', 'country': 'BA', 'website': 'https://www.addiko-rs.ba'},
    {'name': 'MF Banka', 'short_name': 'mf-banka', 'country': 'BA', 'website': 'https://www.mfbanka.com'},
    {'name': 'NLB Banka Banja Luka', 'short_name': 'nlb-bl', 'country': 'BA', 'website': 'https://www.nlbbl.com'},
]

SAMPLE_RATES = [
    # (short_name, loan_type, rate, ert, currency)
    ('intesa-bh', 'stambeni', 3.90, 4.15, 'BAM'),
    ('intesa-bh', 'gotovinski', 6.50, 6.98, 'BAM'),
    ('intesa-bh', 'penzionerski', 5.99, 6.40, 'BAM'),
    ('addiko-fbih', 'gotovinski', 7.99, 8.65, 'BAM'),
    ('addiko-fbih', 'auto', 5.99, 6.45, 'BAM'),
    ('asa-bh', 'stambeni', 4.25, 4.50, 'BAM'),
    ('asa-bh', 'gotovinski', 7.50, 8.10, 'BAM'),
    ('procredit-bh', 'stambeni', 4.00, 4.30, 'BAM'),
    ('procredit-bh', 'gotovinski', 7.00, 7.55, 'BAM'),
    ('union-bh', 'stambeni', 4.50, 4.80, 'BAM'),
    ('union-bh', 'gotovinski', 7.75, 8.30, 'BAM'),
    ('bbi-bh', 'stambeni', 4.20, 4.45, 'BAM'),
    ('bbi-bh', 'gotovinski', 7.25, 7.80, 'BAM'),
    ('ziraat-bh', 'stambeni', 3.95, 4.20, 'BAM'),
    ('ziraat-bh', 'gotovinski', 6.99, 7.50, 'BAM'),
    ('atos-rs-ba', 'stambeni', 4.49, 4.75, 'BAM'),
    ('atos-rs-ba', 'gotovinski', 7.49, 8.10, 'BAM'),
    ('atos-rs-ba', 'auto', 5.99, 6.50, 'BAM'),
    ('nova-banka', 'stambeni', 4.25, 4.55, 'BAM'),
    ('nova-banka', 'gotovinski', 7.99, 8.60, 'BAM'),
    ('addiko-rs-ba', 'gotovinski', 8.25, 9.00, 'BAM'),
    ('mf-banka', 'gotovinski', 8.50, 9.20, 'BAM'),
    ('nlb-bl', 'stambeni', 4.10, 4.40, 'BAM'),
    ('nlb-bl', 'gotovinski', 7.25, 7.85, 'BAM'),
]


def add_banks_and_rates(apps, schema_editor):
    Bank = apps.get_model('calculators', 'Bank')
    InterestRateOffer = apps.get_model('calculators', 'InterestRateOffer')

    bank_map = {}
    for b in NEW_BANKS:
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


def remove_banks(apps, schema_editor):
    Bank = apps.get_model('calculators', 'Bank')
    Bank.objects.filter(short_name__in=[b['short_name'] for b in NEW_BANKS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('calculators', '0002_seed_banks_and_rates'),
    ]

    operations = [
        migrations.RunPython(add_banks_and_rates, remove_banks),
    ]
