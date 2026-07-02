from __future__ import annotations

import hashlib
import hmac
import secrets


def hash_password(password: str, salt: str | None = None) -> str:
	"""Return a salted PBKDF2 hash in the format salt$hash."""
	current_salt = salt or secrets.token_hex(16)
	derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), current_salt.encode("utf-8"), 120_000)
	return f"{current_salt}${derived.hex()}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
	"""Validate a plain password against the stored salt$hash format."""
	try:
		salt, digest = stored_hash.split("$", maxsplit=1)
	except ValueError:
		return False

	computed = hash_password(plain_password, salt)
	return hmac.compare_digest(computed, f"{salt}${digest}")


def generate_access_token(prefix: str = "gov") -> str:
	"""Generate a random token for temporary app/session identification."""
	return f"{prefix}_{secrets.token_urlsafe(24)}"

