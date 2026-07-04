"""
llm_client.py
-------------
This file has ONE job: send a prompt to the Gemini model and return the text reply.
It is the only place in the whole project that talks directly to the AI model.
"""

import os
from google import genai
from dotenv import load_dotenv

# Load the variables from the .env file (so GEMINI_API_KEY becomes available)
load_dotenv()

# Read the API key from the environment. We never write the key directly in the code.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Create the Gemini client once, using our key.
client = genai.Client(api_key=GEMINI_API_KEY)

# The model we use. "flash" is fast and cheap, which is perfect for a proof of concept.
MODEL_NAME = "gemini-2.5-flash"


def get_answer(prompt: str) -> str:
    """
    Send a prompt (a string) to Gemini and return the model's text answer.
    """
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )
    return response.text


# This block only runs if you run THIS file directly (python llm_client.py).
# It lets you test that Gemini responds, before building anything else.
if __name__ == "__main__":
    test_answer = get_answer("Say hello in Kinyarwanda.")
    print("Gemini replied:")
    print(test_answer)