from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class IntentResult:
    intent: str
    service_name: str | None
    confidence: float


# Keys map to the exact Service.name values stored in the database.
KEYWORD_TO_SERVICE: dict[str, str] = {
    # Application for National ID
    "national id": "Application for National ID",
    "national identity": "Application for National ID",
    "identity card": "Application for National ID",
    "citizen application number": "Application for National ID",
    "indangamuntu": "Application for National ID",
    "iryangamuntu": "Application for National ID",
    "carte d'identite": "Application for National ID",
    "carte didentite": "Application for National ID",
    "identite nationale": "Application for National ID",

    # Birth Certificate (specific: certificate for an EXISTING birth record)
    "birth certificate": "Birth Certificate",
    "certificate of birth": "Birth Certificate",
    "icyemezo cy'amavuko": "Birth Certificate",
    "icyemezo cyamavuko": "Birth Certificate",
    "acte de naissance": "Birth Certificate",

    # Birth Record (registering a NEW birth; also the generic fallback
    # for bare "birth"/"amavuko"/"naissance" without a qualifier)
    "birth record": "Birth Record",
    "birth registration": "Birth Record",
    "register a birth": "Birth Record",
    "kwandikisha amavuko": "Birth Record",
    "enregistrement de naissance": "Birth Record",
    "amavuko": "Birth Record",
    "naissance": "Birth Record",

    # Mutuelle (Health Insurance) Renewal
    "mutuelle": "Mutuelle (Health Insurance) Renewal",
    "health insurance": "Mutuelle (Health Insurance) Renewal",
    "community based health insurance": "Mutuelle (Health Insurance) Renewal",
    "ubwishingizi bw'ubuzima": "Mutuelle (Health Insurance) Renewal",
    "ubwishingizi bwubuzima": "Mutuelle (Health Insurance) Renewal",
    "ubwishingizi": "Mutuelle (Health Insurance) Renewal",
    "assurance maladie": "Mutuelle (Health Insurance) Renewal",
    "assurance sante": "Mutuelle (Health Insurance) Renewal",

    # Marriage Declaration (declaring an upcoming marriage)
    "marriage declaration": "Marriage Declaration",
    "declare marriage": "Marriage Declaration",
    "kwiyandikisha ku bukwe": "Marriage Declaration",
    "icyemezo cy'ubukwe": "Marriage Declaration",
    "icyemezo cyubukwe": "Marriage Declaration",
    "ubukwe": "Marriage Declaration",
    "wedding": "Marriage Declaration",
    "get married": "Marriage Declaration",
    "acte de mariage": "Marriage Declaration",
    "certificat de mariage": "Marriage Declaration",
    "mariage": "Marriage Declaration",
    "marriage": "Marriage Declaration",
    "declare a marriage": "Marriage Declaration",

    # Driving License Application
    "driving license": "Driving License Application",
    "driving licence": "Driving License Application",
    "driver's license": "Driving License Application",
    "uruhushya rwo gutwara imodoka": "Driving License Application",
    "uruhushya rwo gutwara": "Driving License Application",
    "gutwara imodoka": "Driving License Application",
    "permis de conduire": "Driving License Application",
    "permis": "Driving License Application",
}

GREETING_TOKENS = [
    "muraho", "hello", "hi", "hey", "bwakeye", "mwiriwe",
    "amakuru", "bite", "bonjour", "salut",
]

HELP_TOKENS = [
    "help", "assist", "how", "nkeneye", "ifasha", "ngomba",
    "ndashaka", "nkenera", "mbaza", "saba", "ubufasha",
    "guidance", "guide", "aide", "comment",
]


def _find_service_match(normalized: str, available_services: list[str] | None) -> tuple[str | None, float]:
    """
    Find the most specific (longest) keyword match using word-boundary
    matching, so short substrings can't false-positive inside other words.
    """
    for keyword in sorted(KEYWORD_TO_SERVICE.keys(), key=len, reverse=True):
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, normalized):
            service_name = KEYWORD_TO_SERVICE[keyword]
            if available_services and service_name not in available_services:
                continue
            return service_name, 0.82
    return None, 0.0


def detect_intent(message: str, available_services: list[str] | None = None) -> IntentResult:
    normalized = message.strip().lower()

    # Check for a service match FIRST, so messages like "Hello, I need a
    # national ID" still correctly detect the service instead of being
    # swallowed by the greeting check.
    matched_service, confidence = _find_service_match(normalized, available_services)
    if matched_service:
        return IntentResult(intent="start_service", service_name=matched_service, confidence=confidence)

    if any(re.search(r'\b' + re.escape(token) + r'\b', normalized) for token in GREETING_TOKENS):
        return IntentResult(intent="greeting", service_name=None, confidence=0.95)

    if any(re.search(r'\b' + re.escape(token) + r'\b', normalized) for token in HELP_TOKENS):
        return IntentResult(intent="support_request", service_name=None, confidence=0.7)

    return IntentResult(intent="general_query", service_name=None, confidence=0.55)


YES_TOKENS = [
    "yes", "yego", "oui", "yeah", "sure", "okay", "ok", "proceed",
    "continue", "tangira", "reka tugende", "yee",
]

NO_TOKENS = [
    "no", "oya", "non", "nope", "cancel", "reka", "ntabwo", "ntago",
]


def detect_confirmation(message: str) -> str | None:
    """
    Detects a yes/no confirmation in Kinyarwanda, English, or French.
    Returns 'yes', 'no', or None if the message isn't a clear confirmation.
    """
    normalized = message.strip().lower()

    if any(re.search(r'\b' + re.escape(token) + r'\b', normalized) for token in NO_TOKENS):
        return "no"
    if any(re.search(r'\b' + re.escape(token) + r'\b', normalized) for token in YES_TOKENS):
        return "yes"
    return None


SKIP_TOKENS = [
    "skip", "none", "n/a", "na", "nta", "ntabwo mfite", "sinabifite",
    "i don't have", "i dont have", "don't have one", "dont have one",
    "not applicable", "ntacyo",
]


def detect_skip(message: str) -> bool:
    """
    Detects whether the user wants to skip an optional requirement.
    """
    normalized = message.strip().lower()
    return any(token in normalized for token in SKIP_TOKENS)
