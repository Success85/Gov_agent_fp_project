from __future__ import annotations

import re
from datetime import datetime

# Rwanda's 30 districts across 5 provinces. This is small, stable, public
# administrative data. Sector-level validation (~416 sectors) is
# intentionally NOT included here: a hardcoded sector list risks being
# incomplete or inaccurate without a verified authoritative source, so
# sector fields remain free text pending a properly sourced dataset.
RWANDA_DISTRICTS = {
    # Kigali City
    "gasabo", "kicukiro", "nyarugenge",
    # Southern Province
    "gisagara", "huye", "kamonyi", "muhanga", "nyamagabe",
    "nyanza", "nyaruguru", "ruhango",
    # Western Province
    "karongi", "ngororero", "nyabihu", "nyamasheke",
    "rubavu", "rusizi", "rutsiro",
    # Northern Province
    "burera", "gakenke", "gicumbi", "musanze", "rulindo",
    # Eastern Province
    "bugesera", "gatsibo", "kayonza", "kirehe",
    "ngoma", "nyagatare", "rwamagana",
}


def validate_national_id(value: str, language: str = "en") -> tuple[bool, str | None]:
    """
    Validates that a Rwandan National ID number is present in the answer.

    Real requirement fields in this system are phrased as "ID Type and
    Number" (e.g. "National ID: 1198800111222333" or just the bare
    number), so this extracts any 16-digit sequence found in the answer
    rather than requiring the entire input to be exactly 16 digits.

    A valid Rwandan National ID has 16 digits: 1 status digit + 4-digit
    birth year + 1 gender digit + 7-digit sequence + 1 reissue digit +
    2 security digits.

    This checks FORMAT only - it cannot and does not verify that the
    number belongs to a real, registered citizen, since that would
    require access to NIDA's restricted database, which is not available.

    Returns (is_valid, error_message).
    """
    digit_runs = re.findall(r"\d+", value)
    sixteen_digit_runs = [run for run in digit_runs if len(run) == 16]

    messages = {
        "missing": {
            "rw": "Nyamuneka wandike nomero y'Indangamuntu ifite imibare 16 (urugero: 1198800111222333).",
            "fr": "Veuillez inclure un num\u00e9ro de carte d'identit\u00e9 nationale valide \u00e0 16 chiffres (ex. 1198800111222333).",
            "en": "Please include a valid 16-digit National ID number (e.g. 1198800111222333).",
        },
        "implausible": {
            "rw": "Iyi nomero ntisa n'iy'Indangamuntu yemewe \u2014 umwaka wavukiyemo ntusa n'ukuri.",
            "fr": "Ce num\u00e9ro ne ressemble pas \u00e0 un num\u00e9ro de carte d'identit\u00e9 valide \u2014 l'ann\u00e9e de naissance semble incorrecte.",
            "en": "That doesn't look like a valid National ID number \u2014 the birth-year portion seems implausible.",
        },
    }

    if not sixteen_digit_runs:
        return False, messages["missing"].get(language, messages["missing"]["en"])

    current_year = datetime.utcnow().year
    for candidate in sixteen_digit_runs:
        birth_year = int(candidate[1:5])
        if 1900 <= birth_year <= current_year:
            return True, None

    return False, messages["implausible"].get(language, messages["implausible"]["en"])


def validate_district(value: str, language: str = "en") -> tuple[bool, str | None]:
    """
    Validates that a district name matches one of Rwanda's 30 real
    administrative districts (case-insensitive).

    Returns (is_valid, error_message).
    """
    candidate = value.strip().lower()

    if candidate in RWANDA_DISTRICTS:
        return True, None

    messages = {
        "rw": f"'{value.strip()}' ntabwo ari akarere kabaho muri u Rwanda. Nyamuneka tanga kamwe mu turere 30 (urugero: Gasabo, Huye, Musanze, Rubavu).",
        "fr": f"'{value.strip()}' ne correspond \u00e0 aucun district rwandais r\u00e9el. Veuillez indiquer l'un des 30 districts (ex. Gasabo, Huye, Musanze, Rubavu).",
        "en": f"'{value.strip()}' doesn't match a real Rwandan district. Please provide one of Rwanda's 30 districts (e.g. Gasabo, Huye, Musanze, Rubavu).",
    }
    return False, messages.get(language, messages["en"])


VALIDATORS = {
    "national_id": validate_national_id,
    "district": validate_district,
}


def validate_field(validation_type: str | None, value: str, language: str = "en") -> tuple[bool, str | None]:
    """
    Dispatches to the correct validator based on validation_type.
    Returns (True, None) if there is no validator configured for this
    field (i.e. free text is accepted as-is).
    """
    if not validation_type:
        return True, None

    validator = VALIDATORS.get(validation_type)
    if validator is None:
        return True, None

    return validator(value, language)


DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%d %B %Y", "%B %d, %Y", "%B %d %Y"]


def _parse_date(value: str):
    candidate = value.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(candidate, fmt).date()
        except ValueError:
            continue
    return None


def validate_marriage_date_21_days(value: str, language: str = "en") -> tuple[bool, str | None]:
    """
    Validates that the given date is at least 21 days from today, matching
    Rwanda's legal notice period for civil marriage declarations.
    """
    messages = {
        "unparsed": {
            "rw": "Ntibyashobotse gusoma iyi tariki. Nyamuneka wandike nk'aya: 2026-08-15.",
            "fr": "Impossible de lire cette date. Veuillez l'\u00e9crire comme ceci\u00a0: 2026-08-15.",
            "en": "That date couldn't be read. Please write it like this: 2026-08-15.",
        },
        "too_soon": {
            "rw": "Itariki y'ubukwe igomba kuba nibura iminsi 21 uhereye uyu munsi. Nyamuneka hitamo indi tariki.",
            "fr": "La date du mariage doit \u00eatre au moins 21 jours \u00e0 partir d'aujourd'hui. Veuillez choisir une autre date.",
            "en": "The marriage date must be at least 21 days from today. Please choose a later date.",
        },
    }

    parsed = _parse_date(value)
    if parsed is None:
        return False, messages["unparsed"].get(language, messages["unparsed"]["en"])

    days_from_today = (parsed - datetime.utcnow().date()).days
    if days_from_today < 21:
        return False, messages["too_soon"].get(language, messages["too_soon"]["en"])

    return True, None


VALIDATORS["marriage_date_21_days"] = validate_marriage_date_21_days
