import random


def unique_phone() -> str:
    """
    Generates a valid Rwandan phone number in the required format:
    07[2389]XXXXXXX - matching User.validate_phone_number's real pattern.
    """
    prefix = random.choice(["072", "073", "078", "079"])
    remainder = "".join(str(random.randint(0, 9)) for _ in range(7))
    return f"{prefix}{remainder}"
