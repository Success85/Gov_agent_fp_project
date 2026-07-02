from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IntentResult:
	intent: str
	service_name: str | None
	confidence: float


KEYWORD_TO_SERVICE = {
	"birth": "Birth Certificate",
	"certificate": "Birth Certificate",
	"national id": "National ID",
	"id": "National ID",
	"indangamuntu": "National ID",
	"icyemezo cy'amavuko": "Birth Certificate",
}


def detect_intent(message: str, available_services: list[str] | None = None) -> IntentResult:
	"""Detect a basic user intent and the most likely service from a free-text message."""
	normalized = message.strip().lower()

	if any(token in normalized for token in ["muraho", "hello", "hi"]):
		return IntentResult(intent="greeting", service_name=None, confidence=0.95)

	matched_service: str | None = None
	best_confidence = 0.0

	for keyword, service_name in KEYWORD_TO_SERVICE.items():
		if keyword in normalized:
			if available_services and service_name not in available_services:
				continue
			matched_service = service_name
			best_confidence = max(best_confidence, 0.82)

	if matched_service:
		return IntentResult(intent="start_service", service_name=matched_service, confidence=best_confidence)

	if any(token in normalized for token in ["help", "assist", "how", "nkeneye"]):
		return IntentResult(intent="support_request", service_name=None, confidence=0.7)

	return IntentResult(intent="general_query", service_name=None, confidence=0.55)

