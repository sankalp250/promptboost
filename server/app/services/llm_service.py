import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- TEMPLATES remain the same ---
GENERIC_PROMPT_TEMPLATE = """...""" # Keep this template as is
STRUCTURED_PROMPT_TEMPLATE = """...""" # Keep this template as is

# --- 2. INITIALIZE LLMS ---
try:
    groq_chat = ChatGroq(
        temperature=0.7,
        groq_api_key=settings.GROQ_API_KEY,
        # --- FIX 1: UPDATED MODEL NAME ---
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

# --- 3. CREATE ENHANCEMENT FUNCTIONS ---
def get_enhanced_prompt_strategy_A(user_prompt: str) -> str | None:
    # ... logic remains the same
    # But you can add more logging if needed
    return "This strategy is not currently used for this user."

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
            # --- FIX 2: Added explicit logging for Gemini ---
            logger.info(f"(B) Attempting enhancement with Gemini...")
            chain = ChatPromptTemplate.from_template(STRUCTURED_PROMPT_TEMPLATE) | gemini_chat | StrOutputParser()
            return chain.invoke({"user_prompt": user_prompt})
        except Exception as e2:
            logger.error(f"(B) Gemini fallback also failed: {e2}")
            # --- This is where 'None' is returned ---
            return None