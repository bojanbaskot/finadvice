"""
Seed migration: BiH media portals with RSS feeds.
Entity codes: FBiH, RS, BD, national
Portal types: online, tv, radio, agency
"""
from django.db import migrations


PORTALS = [
    # name, url, rss_url, entity, portal_type, rak_id
    # ─── National / multi-entity ───────────────────────────────────────────────
    ('Klix.ba', 'https://www.klix.ba', 'https://www.klix.ba/rss/vijesti', 'national', 'online', ''),
    ('Avaz.ba', 'https://avaz.ba', 'https://avaz.ba/rss', 'national', 'online', ''),
    ('Oslobodjenje', 'https://oslobodjenje.ba', 'https://oslobodjenje.ba/rss', 'national', 'online', ''),
    ('N1 BiH', 'https://n1info.ba', 'https://n1info.ba/feed/', 'national', 'tv', ''),
    ('Al Jazeera Balkans', 'https://balkans.aljazeera.net', 'https://balkans.aljazeera.net/rss', 'national', 'tv', ''),
    ('Hayat', 'https://hayat.ba', 'https://hayat.ba/feed/', 'national', 'tv', ''),
    ('Fena', 'https://www.fena.ba', 'https://www.fena.ba/rss', 'national', 'agency', ''),
    ('Srna', 'https://www.srna.rs', 'https://www.srna.rs/rss', 'national', 'agency', ''),
    # ─── FBiH-leaning ──────────────────────────────────────────────────────────
    ('Bljesak.info', 'https://bljesak.info', 'https://bljesak.info/rss', 'FBiH', 'online', ''),
    ('Faktor.ba', 'https://faktor.ba', 'https://faktor.ba/feed/', 'FBiH', 'online', ''),
    ('Fokus.ba', 'https://fokus.ba', 'https://fokus.ba/feed/', 'FBiH', 'online', ''),
    ('Dnevni avaz (portal)', 'https://avaz.ba', 'https://avaz.ba/rss/vijesti', 'FBiH', 'online', ''),
    ('BHT1', 'https://www.bhrt.ba', 'https://www.bhrt.ba/rss/vijesti', 'national', 'tv', ''),
    ('FTV (vijesti)', 'https://vijesti.ba', 'https://vijesti.ba/rss', 'FBiH', 'tv', ''),
    ('Radiosarajevo.ba', 'https://radiosarajevo.ba', 'https://radiosarajevo.ba/rss', 'FBiH', 'radio', ''),
    ('Inforadar.ba', 'https://inforadar.ba', 'https://inforadar.ba/feed/', 'FBiH', 'online', ''),
    # ─── RS-leaning ────────────────────────────────────────────────────────────
    ('RTRS', 'https://rtrs.tv', 'https://rtrs.tv/rss', 'RS', 'tv', ''),
    ('Nezavisne novine', 'https://nezavisne.com', 'https://nezavisne.com/rss', 'RS', 'online', ''),
    ('Glas Srpske', 'https://glassrpske.com', 'https://glassrpske.com/rss', 'RS', 'online', ''),
    ('Banjaluka.com', 'https://www.banjaluka.com', 'https://www.banjaluka.com/feed/', 'RS', 'online', ''),
    ('Capital.ba', 'https://capital.ba', 'https://capital.ba/feed/', 'RS', 'online', ''),
    ('Patria.ba', 'https://patria.ba', 'https://patria.ba/feed/', 'RS', 'online', ''),
]


def seed_portals(apps, schema_editor):
    MediaPortal = apps.get_model('politics', 'MediaPortal')
    for name, url, rss_url, entity, portal_type, rak_id in PORTALS:
        MediaPortal.objects.get_or_create(
            name=name,
            defaults={
                'url': url,
                'rss_url': rss_url,
                'entity': entity,
                'portal_type': portal_type,
                'rak_id': rak_id,
                'is_active': True,
            }
        )


def remove_portals(apps, schema_editor):
    MediaPortal = apps.get_model('politics', 'MediaPortal')
    names = [p[0] for p in PORTALS]
    MediaPortal.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('politics', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_portals, remove_portals),
    ]
