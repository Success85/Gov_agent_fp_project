"""Seed the database with the first verified government-service records."""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.database import SessionLocal, init_db
from app.models.service import Requirement, Service, Step


DEFAULT_SEED_DATA = [
	{
		"name": "Birth Certificate",
		"description": "Request or apply for a birth certificate through the government service flow.",
		"fee": 0,
		"requirements": [
			{
				"name": "Applicant identity details",
				"description": "Full name, date of birth, and contact information.",
				"mandatory": True,
				"needs_upload": False,
				"order_index": 1,
			},
			{
				"name": "Supporting document",
				"description": "Any required supporting file for the service request.",
				"mandatory": False,
				"needs_upload": True,
				"order_index": 2,
			},
		],
		"steps": [
			{"order_index": 1, "description": "Confirm the service request and user details."},
			{"order_index": 2, "description": "Provide required information and documents."},
			{"order_index": 3, "description": "Submit and track the application."},
		],
	},
	{
		"name": "National ID",
		"description": "Apply for or renew a national identity service request.",
		"fee": 0,
		"requirements": [
			{
				"name": "Identity details",
				"description": "Name, national ID number if available, and contact information.",
				"mandatory": True,
				"needs_upload": False,
				"order_index": 1,
			},
			{
				"name": "Photo or supporting file",
				"description": "Upload any required identity support file.",
				"mandatory": False,
				"needs_upload": True,
				"order_index": 2,
			},
		],
		"steps": [
			{"order_index": 1, "description": "Start the identity service request."},
			{"order_index": 2, "description": "Submit personal details and any needed files."},
			{"order_index": 3, "description": "Complete submission and wait for feedback."},
		],
	},
]


def _project_root() -> Path:
	return Path(__file__).resolve().parents[3]


def _seed_source() -> list[dict]:
	seed_file = _project_root() / "data" / "seed_data.json"
	if seed_file.exists() and seed_file.stat().st_size > 0:
		with seed_file.open("r", encoding="utf-8") as handle:
			return json.load(handle)
	return DEFAULT_SEED_DATA


def seed_database(db: Session) -> None:
	for service_payload in _seed_source():
		service = db.query(Service).filter(Service.name == service_payload["name"]).one_or_none()
		if service is None:
			service = Service(
				name=service_payload["name"],
				description=service_payload.get("description"),
				fee=service_payload.get("fee", 0),
			)
			db.add(service)
			db.flush()

		for requirement_payload in service_payload.get("requirements", []):
			requirement = (
				db.query(Requirement)
				.filter(Requirement.service_id == service.id, Requirement.name == requirement_payload["name"])
				.one_or_none()
			)
			if requirement is None:
				requirement = Requirement(
					service_id=service.id,
					name=requirement_payload["name"],
					description=requirement_payload.get("description"),
					mandatory=requirement_payload.get("mandatory", True),
					needs_upload=requirement_payload.get("needs_upload", False),
					order_index=requirement_payload.get("order_index", 0),
				)
				db.add(requirement)

		for step_payload in service_payload.get("steps", []):
			step = (
				db.query(Step)
				.filter(Step.service_id == service.id, Step.order_index == step_payload["order_index"])
				.one_or_none()
			)
			if step is None:
				step = Step(
					service_id=service.id,
					order_index=step_payload["order_index"],
					description=step_payload["description"],
				)
				db.add(step)

	db.commit()


def seed_all() -> None:
	init_db()
	db = SessionLocal()
	try:
		seed_database(db)
	finally:
		db.close()


if __name__ == "__main__":
	seed_all()

