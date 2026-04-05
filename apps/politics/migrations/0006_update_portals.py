"""
Update portal list:
- Deactivate Al Jazeera Balkans (not BiH-specific, blocks scraping)
- Add more BiH portals with confirmed RSS feeds
"""
from django.db import migrations


NEW_PORTALS = [
    # name, url, rss_url, entity, portal_type
    ('Depo.ba', 'https://depo.ba', 'https://depo.ba/rss.xml', 'FBiH', 'online'),
    ('Vijesti.ba', 'https://vijesti.ba', 'https://vijesti.ba/rss', 'FBiH', 'online'),
    ('Slobodna Bosna', 'https://slobodna-bosna.ba', 'https://slobodna-bosna.ba/feed/', 'national', 'online'),
    ('Buka.com', 'https://www.buka.com', 'https://www.buka.com/rss.xml', 'national', 'online'),
    ('Hercegovina.info', 'https://hercegovina.info', 'https://hercegovina.info/feed/', 'FBiH', 'online'),
    ('6ica.ba', 'https://6ica.ba', 'https://6ica.ba/feed/', 'FBiH', 'online'),
    ('Frontal.rs (BiH)', 'https://frontal.rs', 'https://frontal.rs/feed/', 'RS', 'online'),
    ('Istinomjer', 'https://www.istinomjer.ba', 'https://www.istinomjer.ba/feed/', 'national', 'online'),
]


def update_portals(apps, schema_editor):
    MediaPortal = apps.get_model('politics', 'MediaPortal')

    # Deactivate Al Jazeera — not BiH-specific, blocks automated scraping
    MediaPortal.objects.filter(name='Al Jazeera Balkans').update(is_active=False)

    # Add new portals
    for name, url, rss_url, entity, portal_type in NEW_PORTALS:
        MediaPortal.objects.get_or_create(
            name=name,
            defaults={
                'url': url,
                'rss_url': rss_url,
                'entity': entity,
                'portal_type': portal_type,
                'is_active': True,
            }
        )


def revert_portals(apps, schema_editor):
    MediaPortal = apps.get_model('politics', 'MediaPortal')
    MediaPortal.objects.filter(name='Al Jazeera Balkans').update(is_active=True)
    names = [p[0] for p in NEW_PORTALS]
    MediaPortal.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('politics', '0005_fix_more_rss_urls'),
    ]

    operations = [
        migrations.RunPython(update_portals, revert_portals),
    ]
