import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- TEMPLATE FOR STRATEGY A (Generic Enhancement) ---
# THIS TEMPLATE IS NOW MUCH MORE ROBUST WITH EXAMPLES
GENERIC_PROMPT_TEMPLATE = """
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

# ... (imports and GENERIC_PROMPT_TEMPLATE remain the same) ...

# --- NEW TEMPLATE FOR STRATEGY B (The "Visionary" Enhancement) ---
# THIS REPLACES THE OLD, FLAWED QUESTIONNAIRE TEMPLATE.
STRUCTURED_PROMPT_TEMPLATE = """
You are PromptBoost, an expert AI Product Manager specializing in transforming vague user ideas into actionable, feature-rich prompts.

**CRITICAL RULES:**
1.  **DO NOT BE CONVERSATIONAL.** No greetings or extra chat.
2.  **NEVER ASK QUESTIONS.** Your job is to make creative, insightful assumptions and build upon the user's idea.
3.  **YOUR OUTPUT MUST BE ONLY THE ENHANCED PROMPT.** No preambles.
4.  Focus on the 'what' and 'why' – user benefits, core features, and a high-level vision.

**EXAMPLES OF YOUR TASK:**
---
**Vague User Prompt:** add a login page
**Your Output:** Create a modern and user-friendly authentication experience for our web application. Design a clean, responsive login page that includes options for email/password sign-in as well as social login via Google and GitHub. Upon successful authentication, redirect users to their personalized dashboard.
---
**Vague User Prompt:** make a weather app
**Your Output:** Develop a beautiful, intuitive weather application that provides a delightful user experience. The app's main screen should display the current temperature, a descriptive icon (e.g., sunny, rainy), and the high/low for the day. Include a 7-day forecast view and use subtle animations to make the interface feel alive. Prioritize a minimalist design and fast loading times.
---

**VAGUE USER PROMPT:**
{user_prompt}

**YOUR OUTPUT (VISIONARY ENHANCED PROMPT ONLY):**
"""


# --- The rest of the file (LLM initializations and enhancement functions) remains exactly the same ---
# ... (no other changes are needed in this file) ...

# --- 2. INITIALIZE THE LLM PROVIDERS (No changes needed here) ---
try:
    groq_chat = ChatGroq(
        temperature=0.7,
        groq_api_key=settings.GROQ_API_KEY,
        model_name="llama-3.1-8b-instant"
    )
    gemini_chat = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest",
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.7
    )
    logger.info("Successfully initialized both Groq and Gemini models.")
except Exception as e:
    logger.error(f"CRITICAL: Failed to initialize LLMs: {e}")
    groq_chat = None
    gemini_chat = None

# --- 3. CREATE THE CORE ENHANCEMENT FUNCTIONS (No code changes needed, they use the new templates) ---
def get_enhanced_prompt_strategy_A(user_prompt: str) -> str | None:
    if not groq_chat or not gemini_chat:
        return "Server configuration error."
    try:
        logger.info(f"(A) Attempting enhancement with Groq...")
        chain = ChatPromptTemplate.from_template(GENERIC_PROMPT_TEMPLATE) | groq_chat | StrOutputParser()
        return chain.invoke({"user_prompt": user_prompt})
    except Exception as e:
        logger.warning(f"(A) Groq failed: {e}. Falling back to Gemini.")
        try:
            chain = ChatPromptTemplate.from_template(GENERIC_PROMPT_TEMPLATE) | gemini_chat | StrOutputParser()
            return chain.invoke({"user_prompt": user_prompt})
        except Exception as e2:
            logger.error(f"(A) Gemini fallback also failed: {e2}")
            return None

def get_enhanced_prompt_strategy_B(user_prompt: str) -> str | None:
    if not groq_chat or not gemini_chat:
        return "Server configuration error."
    try:
        logger.info(f"(B) Attempting enhancement with Groq...")
        chain = ChatPromptTemplate.from_template(STRUCTURED_PROMPT_TEMPLATE) | groq_chat | StrOutputParser()
        return chain.invoke({"user_prompt": user_prompt})
    except Exception as e:
        logger.warning(f"(B) Groq failed: {e}. Falling back to Gemini.")
        try:
            chain = ChatPromptTemplate.from_template(STRUCTURED_PROMPT_TEMPLATE) | gemini_chat | StrOutputParser()
            return chain.invoke({"user_prompt": user_prompt})
        except Exception as e2:
            logger.error(f"(B) Gemini fallback also failed: {e2}")
            return None