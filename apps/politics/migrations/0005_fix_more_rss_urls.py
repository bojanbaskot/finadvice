"""
Fix RSS URLs for working portals, disable portals without accessible RSS.
- Al Jazeera Balkans: correct URL to /rss.xml
- Patria.ba: correct URL to /rss.xml
- Oslobodjenje: correct URL to /rss.xml
- Bljesak, Faktor, Hayat: Next.js SPA, no RSS — clear rss_url
- RTRS, BHT1: no accessible RSS — clear rss_url
"""
from django.db import migrations


def fix_urls(apps, schema_editor):
    MediaPortal = apps.get_model('politics', 'MediaPortal')

    # Fix working portals with wrong URL
    MediaPortal.objects.filter(name='Al Jazeera Balkans').update(
        rss_url='https://balkans.aljazeera.net/rss.xml'
    )
    MediaPortal.objects.filter(name='Patria.ba').update(
        rss_url='https://patria.ba/rss.xml'
    )
    MediaPortal.objects.filter(name='Oslobodjenje').update(
        rss_url='https://oslobodjenje.ba/rss.xml'
    )

    # Clear RSS for portals that are SPA/have no accessible feed
    no_rss = ['Bljesak.info', 'Faktor.ba', 'Hayat', 'RTRS', 'BHT1']
    MediaPortal.objects.filter(name__in=no_rss).update(rss_url='')


def revert_urls(apps, schema_editor):
    MediaPortal = apps.get_model('politics', 'MediaPortal')
    MediaPortal.objects.filter(name='Al Jazeera Balkans').update(
        rss_url='https://balkans.aljazeera.net/rss'
    )
    MediaPortal.objects.filter(name='Patria.ba').update(
        rss_url='https://patria.ba/feed/'
    )
    MediaPortal.objects.filter(name='Oslobodjenje').update(
        rss_url='https://oslobodjenje.ba/rss'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('politics', '0004_fix_rss_urls'),
    ]

    operations = [
        migrations.RunPython(fix_urls, revert_urls),
    ]
