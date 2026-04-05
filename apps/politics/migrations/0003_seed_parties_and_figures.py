"""
Seed migration: BiH political parties and major political figures.
Entity codes: BiH, FBiH, RS, BD
"""
from django.db import migrations
from django.utils.text import slugify


# (name, abbreviation, entity, ideology, cik_id, website)
PARTIES = [
    # ─── Bošnjački/Citizens ────────────────────────────────────────────────────
    ('Stranka demokratske akcije', 'SDA', 'BiH', 'Konzervativizam, islamska demokratija', '', 'https://www.sda.ba'),
    ('Narod i pravda', 'NiP', 'FBiH', 'Liberalna demokracija', '', 'https://www.narodipravda.ba'),
    ('Demokratska fronta', 'DF', 'FBiH', 'Socijaldemokracija', '', 'https://www.demokratskafronta.ba'),
    ('Socijaldemokratska partija BiH', 'SDP BiH', 'BiH', 'Socijaldemokracija', '', 'https://www.sdp.ba'),
    ('Naša stranka', 'NS', 'BiH', 'Liberalizam, progresivizam', '', 'https://www.nasastranka.ba'),
    ('Bosanska stranka', 'BOSS', 'BiH', 'Bosanska demokratija', '', ''),
    ('Stranka za BiH', 'SBiH', 'BiH', 'Demokratski konzervativizam', '', ''),
    # ─── Srpske stranke ────────────────────────────────────────────────────────
    ('Savez nezavisnih socijaldemokrata', 'SNSD', 'RS', 'Socijaldemokracija, srpski nacionalizam', '', 'https://www.snsd.org'),
    ('Srpska demokratska stranka', 'SDS', 'RS', 'Konzervativizam, srpski nacionalizam', '', 'https://www.sdsrs.ba'),
    ('Partija demokratskog progresa', 'PDP', 'RS', 'Konzervativni liberalizam', '', 'https://www.pdp.org.ba'),
    ('Demokratski narodni savez', 'DNS', 'RS', 'Srpski konzervativizam', '', ''),
    ('Ujedinjena Srpska', 'US', 'RS', 'Srpski nacionalizam', '', ''),
    # ─── Hrvatskih stranke ─────────────────────────────────────────────────────
    ('Hrvatska demokratska zajednica BiH', 'HDZ BiH', 'FBiH', 'Kršćanska demokracija, hrvatsko-nacionalizam', '', 'https://www.hdzbih.org'),
    ('Hrvatska demokratska zajednica 1990', 'HDZ 1990', 'FBiH', 'Kršćanska demokracija', '', ''),
    ('Hrvatska stranka prava', 'HSP', 'FBiH', 'Hrvatski nacionalizam', '', ''),
]

# (name, party_abbr, entity, current_position, name_variations, cik_id, running_for)
FIGURES = [
    # SDA
    ('Bakir Izetbegović', 'SDA', 'BiH', 'Predsjednik SDA', 'Bakir, Izetbegović, B. Izetbegović', '', ''),
    ('Elmedin Konaković', 'NiP', 'BiH', 'Ministar vanjskih poslova BiH', 'Konaković, Elmedin', '', ''),
    # SNSD / RS leadership
    ('Milorad Dodik', 'SNSD', 'RS', 'Član Predsjedništva BiH (srpski)', 'Dodik, M. Dodik', '', ''),
    ('Željka Cvijanović', 'SNSD', 'RS', 'Predsjednica RS', 'Cvijanović, Željka', '', ''),
    ('Radovan Višković', 'SNSD', 'RS', 'Predsjednik Vlade RS', 'Višković, Radovan', '', ''),
    # SDS
    ('Mirko Šarović', 'SDS', 'RS', 'Predsjednik SDS', 'Šarović, Mirko', '', ''),
    # HDZ BiH
    ('Dragan Čović', 'HDZ BiH', 'FBiH', 'Predsjednik HDZ BiH, Predsjedavajući Predsjedništva BiH', 'Čović, Dragan, D. Čović', '', ''),
    # SDP
    ('Nermin Nikšić', 'SDP BiH', 'FBiH', 'Premijer FBiH', 'Nikšić, Nermin', '', ''),
    # DF
    ('Željko Komšić', 'DF', 'BiH', 'Član Predsjedništva BiH (bošnjačko-hrvatski)', 'Komšić, Željko', '', ''),
    # DNS
    ('Nenad Nešić', 'SDS', 'RS', 'Ministar civilnih poslova BiH', 'Nešić, Nenad', '', ''),
    # Naša stranka
    ('Predrag Kojović', 'NS', 'BiH', 'Poslanik u Parlamentarnoj skupštini BiH', 'Kojović, Predrag', '', ''),
    # PDP
    ('Branislav Borenović', 'PDP', 'RS', 'Predsjednik PDP', 'Borenović, Branislav', '', ''),
]


def seed_parties_and_figures(apps, schema_editor):
    PoliticalParty = apps.get_model('politics', 'PoliticalParty')
    PoliticalFigure = apps.get_model('politics', 'PoliticalFigure')

    party_map = {}
    for name, abbr, entity, ideology, cik_id, website in PARTIES:
        party, _ = PoliticalParty.objects.get_or_create(
            name=name,
            defaults={
                'abbreviation': abbr,
                'entity': entity,
                'ideology': ideology,
                'cik_id': cik_id,
                'website': website,
                'is_active': True,
            }
        )
        party_map[abbr] = party

    for name, party_abbr, entity, position, variations, cik_id, running_for in FIGURES:
        party = party_map.get(party_abbr)
        base_slug = slugify(name)
        slug = base_slug
        counter = 1
        while PoliticalFigure.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{counter}'
            counter += 1

        PoliticalFigure.objects.get_or_create(
            name=name,
            defaults={
                'slug': slug,
                'party': party,
                'entity': entity,
                'current_position': position,
                'name_variations': variations,
                'cik_id': cik_id,
                'running_for': running_for,
                'is_active': True,
            }
        )


def remove_parties_and_figures(apps, schema_editor):
    PoliticalParty = apps.get_model('politics', 'PoliticalParty')
    PoliticalFigure = apps.get_model('politics', 'PoliticalFigure')
    abbrs = [p[1] for p in PARTIES]
    names = [f[0] for f in FIGURES]
    PoliticalFigure.objects.filter(name__in=names).delete()
    PoliticalParty.objects.filter(abbreviation__in=abbrs).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('politics', '0002_seed_portals'),
    ]

    operations = [
        migrations.RunPython(seed_parties_and_figures, remove_parties_and_figures),
    ]
