"""Fix RSS URLs for Klix.ba and Nezavisne novine."""
from django.db import migrations


def fix_urls(apps, schema_editor):
    MediaPortal = apps.get_model('politics', 'MediaPortal')
    MediaPortal.objects.filter(name='Klix.ba').update(rss_url='https://www.klix.ba/rss')
    MediaPortal.objects.filter(name='Nezavisne novine').update(rss_url='https://nezavisne.com/rss/najnovije')


def revert_urls(apps, schema_editor):
    MediaPortal = apps.get_model('politics', 'MediaPortal')
    MediaPortal.objects.filter(name='Klix.ba').update(rss_url='https://www.klix.ba/rss/vijesti')
    MediaPortal.objects.filter(name='Nezavisne novine').update(rss_url='https://nezavisne.com/rss')


class Migration(migrations.Migration):

    dependencies = [
        ('politics', '0003_seed_parties_and_figures'),
    ]

    operations = [
        migrations.RunPython(fix_urls, revert_urls),
    ]
