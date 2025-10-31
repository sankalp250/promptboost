import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- THE WINNING TEMPLATE: THE ENGINEER ---
# We now only need this one template.
ENHANCEMENT_PROMPT_TEMPLATE = """
You are PromptBoost, an expert AI specializing in transforming vague user prompts into detailed, effective prompts for other AI models.

**CRITICAL RULES:**
1.  **DO NOT BE CONVERSATIONAL.** Do not greet the user, ask questions, or provide any conversational text.
2.  **NEVER ANSWER THE USER'S PROMPT DIRECTLY.** Your only job is to rewrite and enhance it.
3.  **YOUR OUTPUT MUST BE ONLY THE ENHANCED PROMPT.** No preamble like "Here is the enhanced prompt:".

**EXAMPLES OF YOUR TASK:**
---
**Vague User Prompt:** fix bug in login
**Your Output:** Debug and resolve the issue in the user authentication flow. Investigate the `login.js` component, check for null reference errors on the user object after social sign-in, and ensure the session token is being correctly stored in browser cookies.
---
**Vague User Prompt:** make a discord bot
**Your Output:** Design and develop a Discord bot using Python with the discord.py library. The bot should have the following features: 1. A '!weather' command to fetch and display the current weather for a specified city using the OpenWeatherMap API. 2. A role-management system where users can self-assign roles using a '!role' command. 3. Logging functionality to record major events in a designated admin channel.
---

**VAGUE USER PROMPT:**
{user_prompt}

**YOUR OUTPUT (ENHANCED PROMPT ONLY):**
"""

# --- Initialize LLMs (Unchanged) ---
try:
    groq_chat = ChatGroq(temperature=0.7, groq_api_key=settings.GROQ_API_KEY, model_name="llama-3.1-8b-instant")
    gemini_chat = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", google_api_key=settings.GOOGLE_API_KEY, temperature=0.7)
    logger.info("Successfully initialized both Groq and Gemini models.")
except Exception as e:
    logger.error(f"CRITICAL: Failed to initialize LLMs: {e}")
    groq_chat = None
    gemini_chat = None


# --- A SINGLE, CONSOLIDATED ENHANCEMENT FUNCTION ---
def get_enhanced_prompt(user_prompt: str) -> str | None:
    """Enhances a prompt using the winning 'Engineer' strategy with a fallback."""
    if not groq_chat or not gemini_chat:
        return "Server configuration error."

    try:
        logger.info(f"Attempting enhancement with Groq...")
        chain = ChatPromptTemplate.from_template(ENHANCEMENT_PROMPT_TEMPLATE) | groq_chat | StrOutputParser()
        return chain.invoke({"user_prompt": user_prompt})
    except Exception as e:
        logger.warning(f"Groq failed: {e}. Falling back to Gemini.")
        try:
            chain = ChatPromptTemplate.from_template(ENHANCEMENT_PROMPT_TEMPLATE) | gemini_chat | StrOutputParser()
            return chain.invoke({"user_prompt": user_prompt})
        except Exception as e2:
            logger.error(f"Gemini fallback also failed: {e2}")
            return None