import os
#from google import genai, types
import time
import logging
from functools import lru_cache
from groq import Groq, RateLimitError, APIConnectionError, APITimeoutError
from src.btc.config import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger(__name__)

# GROQ client
class LLMError(Exception):
    """Any failure talking to the LLM."""

@lru_cache(maxsize=1)
def get_groq_client() :
    groq_api_key = GROQ_API_KEY

    if not groq_api_key:
        raise LLMError("GROQ_API_KEY not set")
    return Groq(api_key=groq_api_key)

# Call Groq
def call_groq(system_prompt, user_prompt, retries = 3):
    client = get_groq_client()

    for attempt in range(1, retries + 1):
        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                model = GROQ_MODEL,
                temperature = 0.3,
                max_completion_tokens = 500,
            )
        except (RateLimitError, APIConnectionError, APITimeoutError) as e:
            if attempt == retries:
                raise LLMError(f"Groq failed after {retries} attempts: {e}") from e
            wait = 2 ** attempt       
            logger.warning("Groq transient error (attempt %d/%d): %s. Retrying in %ds",
                           attempt, retries, e, wait)
            time.sleep(wait)
            continue
        except Exception as e:
            raise LLMError(f"Groq error: {e}") from e

        text = response.choices[0].message.content
        if not text or not text.strip():
            raise LLMError("empty response from Groq")
        return text.strip()

""" # Gemini client 
def get_gemini_client():

    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not set")
    return genai.Client(api_key = gemini_api_key)
# Call gemini
def call_gemini(system_prompt, user_prompt, retries=3):
    client = get_gemini_client()
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.3,
        max_output_tokens=500,
    )

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model = "gemini-3.8-flash",
                contents = user_prompt,
                config = config)
            return response.text

        except Exception as e:
            print(f"Failed to Initialize Gemini client:{e}")
            error = str(e).lower()

            if any(keyword in error for keyword in ("rate", "quota", "429")):
                wait = 3
                print(f"Gemini rate limit hit, waiting {wait}s before retry")

                time.sleep(wait)
                continue

            print(f"Gemini error: {e}")
            raise 

    raise Exception(f"Gemini failed after {retries} retries") """