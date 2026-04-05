"""
Lightweight sentiment analysis for Bosnian/Croatian/Serbian text.
Uses a custom lexicon — no heavy ML models needed.
Returns score (-1.0 negative to +1.0 positive) and label.
"""
import re

# Positive words in B/C/S
POSITIVE = {
    'dobar', 'dobra', 'dobro', 'dobri', 'dobre', 'odlican', 'odlicna', 'odlicno',
    'uspjesan', 'uspjesna', 'uspjesno', 'uspjeh', 'uspjesi', 'pobjeda', 'pobijedio',
    'pobjedila', 'napredak', 'napreduje', 'razvoj', 'rast', 'porast', 'povecanje',
    'pozitivan', 'pozitivna', 'pozitivno', 'konstruktivan', 'konstruktivno',
    'sporazum', 'dogovor', 'saradnja', 'suradnja', 'partnerstvo', 'pomoc',
    'podrska', 'podrska', 'zahvalnost', 'zahvalan', 'hvala', 'bravo',
    'reforma', 'reforme', 'poboljsanje', 'unaprijedjenje', 'unapredenje',
    'investicija', 'investicije', 'ulaganje', 'uloziti', 'izgradnja',
    'otvaranje', 'otvoren', 'demokratija', 'sloboda', 'prava', 'pravda',
    'mir', 'stabilnost', 'siguran', 'sigurnost', 'napredak',
    'efikasnost', 'efikasan', 'transparentnost', 'transparentan',
    'zaposljavanje', 'zaposleni', 'plate', 'penzije', 'socijalna',
    'bolnica', 'skola', 'obrazovanje', 'zdravstvo',
    'rekord', 'historijski', 'znacajan', 'vazno', 'korisno',
    'doprinos', 'postignuce', 'rezultat', 'inicijativa',
    'prihvaceno', 'odobren', 'potvrdjeno', 'izglasano',
    'pohvala', 'nagrada', 'odlikovanje', 'priznanje',
    'pomirenje', 'integracija', 'eu', 'nato', 'evropa',
}

# Negative words in B/C/S
NEGATIVE = {
    'lose', 'losa', 'loso', 'losi', 'los',
    'kriminal', 'kriminalan', 'korupcija', 'koruptan', 'koruptivan',
    'skandal', 'skandalozan', 'afera', 'malverzacija', 'prevara',
    'lazov', 'laz', 'lazni', 'lazna', 'lazno', 'manipulacija',
    'optuzba', 'optuzba', 'optuzen', 'optuzena', 'istrazuje',
    'hapsenje', 'uhapsen', 'uhapsena', 'pritvor', 'zatvor',
    'tuzba', 'sudjenje', 'istraga', 'presuda',
    'nasilje', 'nasilan', 'agresija', 'agresivan', 'prijetnja',
    'kriza', 'problem', 'problemi', 'teskoca', 'teskoci',
    'neuspjeh', 'propast', 'kolaps', 'bankrot',
    'pad', 'smanjenje', 'gubitak', 'deficit',
    'nezaposlenost', 'siromastvo', 'osiromavljenje',
    'blokada', 'blokira', 'sprjecava', 'opstrukcija',
    'podjela', 'sukob', 'konfikt', 'svadja', 'tenzija',
    'nezadovoljstvo', 'protest', 'demonstracija', 'strajk',
    'diskriminacija', 'segregacija', 'neravnopravnost',
    'korupcija', 'mito', 'podmicivanje',
    'vlast', 'autokratija', 'diktatura',  # context-dependent but often negative
    'lobiranje', 'klijentelizam', 'nepotizam',
    'uvredljiv', 'uvrijedio', 'napad', 'napao', 'vridjanje',
    'odbijen', 'odbijena', 'blokiran', 'zabranjen',
    'povlacenje', 'ostavka', 'smijenjen', 'razrijesen',
    'smrt', 'tragicno', 'katastrofa', 'tragedija',
    'sankcija', 'sankcije', 'embargo', 'izolacija',
    'ratni', 'rata', 'vojni', 'oruzje',
}

# Intensifiers multiply score
INTENSIFIERS = {
    'veoma', 'jako', 'izuzetno', 'extremno', 'najgori', 'najbolji',
    'totalni', 'potpuni', 'apsolutni', 'nevjerovatan', 'strasan',
}

# Negators flip sentiment
NEGATORS = {
    'ne', 'nije', 'nisu', 'nikada', 'nikad', 'nema', 'bez', 'ni',
    'nijedan', 'niti', 'nikako',
}


def _tokenize(text):
    return re.findall(r'\b\w+\b', text.lower())


def analyze_sentiment(text):
    """
    Returns (score, label) where score is -1.0 to +1.0.
    label is 'positive', 'negative', or 'neutral'.
    """
    if not text or len(text.strip()) < 5:
        return 0.0, 'neutral'

    tokens = _tokenize(text)
    if not tokens:
        return 0.0, 'neutral'

    score = 0.0
    i = 0
    while i < len(tokens):
        token = tokens[i]
        # Check window before token for negator
        window = tokens[max(0, i-2):i]
        negated = any(w in NEGATORS for w in window)
        intensified = any(w in INTENSIFIERS for w in window)
        multiplier = 1.5 if intensified else 1.0

        if token in POSITIVE:
            delta = 1.0 * multiplier
            score += -delta if negated else delta
        elif token in NEGATIVE:
            delta = 1.0 * multiplier
            score += delta if negated else -delta
        i += 1

    # Normalize to -1..+1
    if score == 0:
        return 0.0, 'neutral'

    normalized = max(-1.0, min(1.0, score / max(len(tokens) / 10, 1)))

    if normalized > 0.05:
        label = 'positive'
    elif normalized < -0.05:
        label = 'negative'
    else:
        label = 'neutral'

    return round(normalized, 4), label


def extract_mention_excerpt(text, name_variants, window_sentences=2):
    """
    Extract sentences around the first mention of any name variant.
    Returns excerpt string (up to ~500 chars).
    """
    if not text:
        return ''

    sentences = re.split(r'(?<=[.!?])\s+', text)
    for i, sentence in enumerate(sentences):
        for variant in name_variants:
            if variant.lower() in sentence.lower():
                start = max(0, i - 1)
                end = min(len(sentences), i + window_sentences)
                excerpt = ' '.join(sentences[start:end])
                return excerpt[:600]
    return text[:300]
