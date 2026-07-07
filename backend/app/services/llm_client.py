from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class LLMResponse:
	text: str
	model: str = "mock-kinyarwanda-assistant"


KINYARWANDA_GREETING = (
	"Muraho! Ndi umuyobozi wa serivisi za leta. \n\n"
	"Nkwakiriye kuri serivisi z'ibanze za leta. Ushobora kumbaza ikibazo ufite "
	"cyangwa ukore porogaramu ya leta. \n\n"
	"Serivisi zihari: \n"
	"- Icyemezo cy'Amavuko (Birth Certificate)\n"
	"- Indangamuntu (National ID)\n\n"
	"None se nkugirire iki?"
)

SERVICE_INTROS = {
	"National ID": (
		"Nzakuyobora mu gusaba Indangamuntu. \n\n"
		"Ibi bikurikira ni ibyangombwa: \n"
		"1. Amazina yawe, itariki y'amavuko, n'imibare yawe yo kurambana\n"
		"2. Ifoto cyangwa dosiye ishyigikira\n\n"
		"Shyiraho numero ya terefone yawe ngo tubone gutangira."
	),
	"Birth Certificate": (
		"Nzakuyobora mu gusaba Icyemezo cy'Amavuko. \n\n"
		"Ibi bikurikira ni ibyangombwa: \n"
		"1. Amazina yawe, itariki y'amavuko, n'imibare yawe yo kurambana\n"
		"2. Dosiye ishyigikira (niba bisabwa)\n\n"
		"Shyiraho numero ya terefone yawe ngo tubone gutangira."
	),
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

		if "greeting" in intent:
			text = KINYARWANDA_GREETING
		elif info["service"] and info["service"] in SERVICE_INTROS:
			intro = SERVICE_INTROS[info["service"]]
			requirements = info["requirements"].replace("- ", "\n- ")
			fee = info["fee"]
			text = (
				f"{intro}\n\n"
				f"Ibikorwa byose: {requirements}\n\n"
				f"Amafaranga: {fee} RWF\n\n"
				f"Ushaka gukomeza? Emeza cyangwa ugaruke."
			)
		else:
			reqs = info["requirements"].replace("- ", "\n- ")
			text = (
				f"Ndagufasha kuri serivisi ya leta. \n\n"
				f"Ibyangombwa: {reqs}\n\n"
				f"Ese hari ikindi wakwiriza?"
			)

		return LLMResponse(text=text, model=self.model_name)

