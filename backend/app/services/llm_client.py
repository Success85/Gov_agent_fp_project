from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LLMResponse:
	text: str
	model: str = "mock-kinyarwanda-assistant"


class LLMClient:
	"""Lightweight LLM client abstraction.

	This mock implementation keeps development moving even before a real provider key is added.
	"""

	def __init__(self, model_name: str = "mock-kinyarwanda-assistant") -> None:
		self.model_name = model_name

	def generate_reply(self, prompt: str, system_prompt: str | None = None) -> LLMResponse:
		system_note = system_prompt.strip() if system_prompt else "Government service guidance mode"
		trimmed = prompt.strip().replace("\n", " ")
		message = (
			f"[{system_note}] "
			f"Ndagufasha kuri serivisi ya leta. Dushingiye ku makuru yemejwe. "
			f"Incamake y'ikibazo cyawe: {trimmed[:320]}"
		)
		return LLMResponse(text=message, model=self.model_name)

