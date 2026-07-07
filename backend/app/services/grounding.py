from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GroundingContext:
	service_name: str
	description: str | None = None
	fee: float | int = 0
	requirements: list[str] = field(default_factory=list)
	steps: list[str] = field(default_factory=list)
	source: str = "Verified service knowledge base"


SYSTEM_PROMPTS = {
	"rw": (
		"Uri umuyobozi wa serivisi za leta. Subiza ukoresheje amakuru yemejwe gusa. "
		"Niba amakuru adahari, bivuge neza kandi usabe ikindi wakenera."
	),
	"en": (
		"You are a government-service assistant. Answer using only verified context. "
		"If information is missing, say that clearly and ask for the needed details."
	),
}


def build_grounded_prompt(user_message: str, context: GroundingContext, language: str = "rw") -> str:
	requirements_block = "\n".join(f"- {item}" for item in context.requirements) or "- Not provided"
	steps_block = "\n".join(f"{index + 1}. {step}" for index, step in enumerate(context.steps)) or "1. Not provided"
	system_prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["en"])

	return (
		f"{system_prompt}\n"
		f"Service: {context.service_name}\n"
		f"Description: {context.description or 'N/A'}\n"
		f"Fee: {context.fee}\n"
		f"Source: {context.source}\n"
		"Requirements:\n"
		f"{requirements_block}\n"
		"Steps:\n"
		f"{steps_block}\n"
		f"User message: {user_message}\n"
	)

