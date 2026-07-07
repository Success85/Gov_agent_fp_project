from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class LLMResponse:
	text: str
	model: str = "mock-kinyarwanda-assistant"


GREETINGS = {
	"rw": (
		"Muraho! Ndi umuyobozi wa serivisi za leta. \n\n"
		"Nkwakiriye kuri serivisi z'ibanze za leta. Ushobora kumbaza ikibazo ufite "
		"cyangwa ukore porogaramu ya leta. \n\n"
		"Serivisi zihari: \n"
		"- Icyemezo cy'Amavuko (Birth Certificate)\n"
		"- Indangamuntu (National ID)\n\n"
		"None se nkugirire iki?"
	),
	"en": (
		"Hello! I am a government service assistant. \n\n"
		"Welcome to the government services portal. You can ask me a question "
		"or start an application. \n\n"
		"Available services: \n"
		"- Birth Certificate\n"
		"- National ID\n\n"
		"How can I help you?"
	),
}

SERVICE_INTROS = {
	"National ID": {
		"rw": (
			"Nzakuyobora mu gusaba Indangamuntu. \n\n"
			"Ibi bikurikira ni ibyangombwa: \n"
			"1. Amazina yawe, itariki y'amavuko, n'imibare yawe yo kurambana\n"
			"2. Ifoto cyangwa dosiye ishyigikira\n\n"
			"Shyiraho numero ya terefone yawe ngo tubone gutangira."
		),
		"en": (
			"I will guide you through applying for a National ID. \n\n"
			"The following are required: \n"
			"1. Your full name, date of birth, and contact details\n"
			"2. A photo or supporting document\n\n"
			"Please provide your phone number to get started."
		),
	},
	"Birth Certificate": {
		"rw": (
			"Nzakuyobora mu gusaba Icyemezo cy'Amavuko. \n\n"
			"Ibi bikurikira ni ibyangombwa: \n"
			"1. Amazina yawe, itariki y'amavuko, n'imibare yawe yo kurambana\n"
			"2. Dosiye ishyigikira (niba bisabwa)\n\n"
			"Shyiraho numero ya terefone yawe ngo tubone gutangira."
		),
		"en": (
			"I will guide you through applying for a Birth Certificate. \n\n"
			"The following are required: \n"
			"1. Your full name, date of birth, and contact details\n"
			"2. A supporting document (if required)\n\n"
			"Please provide your phone number to get started."
		),
	},
}


def _extract_prompt_info(prompt: str) -> dict:
	service_match = re.search(r"Service:\s*(.+)", prompt)
	desc_match = re.search(r"Description:\s*(.+)", prompt)
	fee_match = re.search(r"Fee:\s*(.+)", prompt)
	req_section = re.search(r"Requirements:\n(.+?)(?=\nSteps:|\nUser message:)", prompt, re.DOTALL)
	steps_section = re.search(r"Steps:\n(.+?)(?=\nUser message:)", prompt, re.DOTALL)
	user_msg_match = re.search(r"User message:\s*(.+)", prompt)

	return {
		"service": service_match.group(1).strip() if service_match else None,
		"description": desc_match.group(1).strip() if desc_match else None,
		"fee": fee_match.group(1).strip() if fee_match else "0",
		"requirements": req_section.group(1).strip() if req_section else "",
		"steps": steps_section.group(1).strip() if steps_section else "",
		"user_message": user_msg_match.group(1).strip() if user_msg_match else "",
	}


class LLMClient:

	def __init__(self, model_name: str = "mock-kinyarwanda-assistant") -> None:
		self.model_name = model_name

	def generate_reply(self, prompt: str, system_prompt: str | None = None) -> LLMResponse:
		info = _extract_prompt_info(prompt)
		intent = (system_prompt or "").strip()

		language = "rw"
		lang_match = re.search(r"Language:\s*(rw|en)", prompt, re.IGNORECASE)
		if lang_match:
			language = lang_match.group(1).lower()

		if "greeting" in intent:
			text = GREETINGS.get(language, GREETINGS["rw"])
		elif info["service"] and info["service"] in SERVICE_INTROS:
			intro = SERVICE_INTROS[info["service"]].get(language, SERVICE_INTROS[info["service"]]["rw"])
			requirements = info["requirements"].replace("- ", "\n- ")
			fee = info["fee"]
			if language == "en":
				text = (
					f"{intro}\n\n"
					f"All steps: {requirements}\n\n"
					f"Fee: {fee} RWF\n\n"
					f"Do you want to continue? Confirm or go back."
				)
			else:
				text = (
					f"{intro}\n\n"
					f"Ibikorwa byose: {requirements}\n\n"
					f"Amafaranga: {fee} RWF\n\n"
					f"Ushaka gukomeza? Emeza cyangwa ugaruke."
				)
		else:
			reqs = info["requirements"].replace("- ", "\n- ")
			if language == "en":
				text = (
					f"Let me help you with this service. \n\n"
					f"Requirements: {reqs}\n\n"
					f"Is there anything else you need?"
				)
			else:
				text = (
					f"Ndagufasha kuri serivisi ya leta. \n\n"
					f"Ibyangombwa: {reqs}\n\n"
					f"Ese hari ikindi wakwiriza?"
				)

		return LLMResponse(text=text, model=self.model_name)

