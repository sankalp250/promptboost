import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import settings
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- HELPER FUNCTION TO DETECT CONTEXT ---
def detect_context(user_prompt):
    """Detects programming context to assign a professional persona."""
    if re.search(r'\b(python|pytest|fastapi|py)\b', user_prompt, re.IGNORECASE):
        return "Act as a Senior Python Developer specializing in Test-Driven Development and FastAPI."
    if re.search(r'\b(javascript|react|js|node|typescript|ts)\b', user_prompt, re.IGNORECASE):
        return "Act as a Full-Stack JavaScript Developer experienced with the MERN stack and TypeScript."
    if re.search(r'\b(stripe|payment|charge|checkout)\b', user_prompt, re.IGNORECASE):
        return "Act as a Senior Backend Engineer experienced with e-commerce payment gateways."
    return "Act as a Senior Software Engineer and AI expert."


# --- THE FINAL, DEFINITIVE PROMPT TEMPLATE ---
# This template is highly structured to force the LLM into a specific output.
ENHANCEMENT_PROMPT_TEMPLATE = """
<INSTRUCTIONS>
You are an expert prompt engineer. Your task is to rewrite a user's vague prompt into a high-quality, professional, and actionable prompt for another AI.
You must follow all rules and imitate the examples perfectly.

<RULE>
-   **Analyze the <user_prompt> and assigned <persona>.**
-   **Identify the user's true intent.** What are they trying to build or solve?
-   **Enrich the prompt** by adding specific technical details, libraries, constraints, and a clear output format.
-   **Your final output must be ONLY the enhanced prompt.** No conversation, no explanations, no preambles, no XML tags.
</RULE>

<EXAMPLES>
<EXAMPLE>
<persona>Act as a Senior Python Developer specializing in Test-Driven Development and FastAPI.</persona>
<user_prompt>Write a pytest test for this function</user_prompt>
<ENHANCED_PROMPT>
Act as a Senior Python Developer with a focus on Test-Driven Development (TDD). I need you to write a complete pytest test file for the `EmailValidator` class I will provide.

Create a file named `test_validators.py`. The test file must include separate pytest functions to cover the following cases:
1.  A valid standard email.
2.  An email with a sub-domain.
3.  An invalid email with no "@" symbol.
4.  An invalid email with no domain name.
5.  An input that is not a string (e.g., `None` or an integer). This should return `False`, not raise an error.
6.  An empty string input.
</ENHANCED_PROMPT>
</EXAMPLE>

<EXAMPLE>
<persona>Act as a Senior Backend Engineer experienced with e-commerce payment gateways.</persona>
<user_prompt>How do I use the Stripe API to charge a user</user_prompt>
<ENHANCED_PROMPT>
Act as a full-stack developer experienced with e-commerce. I am building a checkout page and need the backend code to create a Stripe 'Payment Intent'.

**My Environment:**
-   **Language:** Python 3.11
-   **Framework:** FastAPI

**My Request:**
Write a single FastAPI endpoint at `/create-payment-intent` that:
1.  Accepts a JSON `POST` request with one field: `amount` (e.g., 25.50).
2.  Correctly converts the dollar amount into cents for the Stripe API (e.g., 25.50 -> 2550).
3.  Sets the `currency` to "usd".
4.  Uses the official `stripe` Python library to create a `PaymentIntent`.
5.  Returns a JSON response containing only the `client_secret` from the created Payment Intent.
</ENHANCED_PROMPT>
</EXAMPLE>
</EXAMPLES>

<TASK>
<persona>{persona}</persona>
<user_prompt>{user_prompt}</user_prompt>
<ENHANCED_PROMPT>
</ENHANCED_PROMPT>
</TASK>
"""

# --- Initialize LLMs (WITH SWAPPED PRIORITY) ---
try:
    # --- FIX 2: Gemini is now primary, Groq is backup ---
    primary_llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest",
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.7
    )
    fallback_llm = ChatGroq(
        temperature=0.7,
        groq_api_key=settings.GROQ_API_KEY,
        model_name="gemma-7b-it" # or "llama-3.1-8b-instant" if you prefer
    )
    logger.info("Successfully initialized Gemini (Primary) and Groq (Fallback) models.")
except Exception as e:
    logger.error(f"CRITICAL: Failed to initialize LLMs: {e}")
    primary_llm = None
    fallback_llm = None


# --- A SINGLE, CONSOLIDATED ENHANCEMENT FUNCTION ---
def get_enhanced_prompt(user_prompt: str) -> str | None:
    """Enhances a prompt using the definitive, persona-based template."""
    if not primary_llm or not fallback_llm:
        return "Server configuration error."
    
    persona = detect_context(user_prompt)
    logger.info(f"Detected persona: {persona}")
    
    prompt_template = ChatPromptTemplate.from_template(ENHANCEMENT_PROMPT_TEMPLATE)

    # Invoke the chain with the new, swapped LLM priority
    try:
        logger.info(f"Attempting enhancement with Primary LLM (Gemini)...")
        chain = prompt_template | primary_llm | StrOutputParser()
        return chain.invoke({"user_prompt": user_prompt, "persona": persona})
    except Exception as e:
        logger.warning(f"Primary LLM (Gemini) failed: {e}. Falling back to Groq.")
        try:
            chain = prompt_template | fallback_llm | StrOutputParser()
            return chain.invoke({"user_prompt": user_prompt, "persona": persona})
        except Exception as e2:
            logger.error(f"Fallback LLM (Groq) also failed: {e2}")
            return None