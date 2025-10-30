import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- TEMPLATE FOR STRATEGY A ---
GENERIC_PROMPT_TEMPLATE = """
You are PromptBoost, a world-class AI assistant specialized in enhancing user prompts. Your goal is to take a user's vague idea and transform it into a clear, detailed, and effective prompt for another AI. Do NOT answer the prompt directly. Instead, rewrite it to be better.

RULES:
- Add specific details and context.
- Suggest a format if appropriate (e.g., "in a JSON format").
- Incorporate best practices like asking the AI to "think step-by-step".
- The output MUST be only the enhanced prompt, with no preamble or explanation.

VAGUE USER PROMPT: {user_prompt}
ENHANCED PROMPT:"""

# --- TEMPLATE FOR STRATEGY B ---
STRUCTURED_PROMPT_TEMPLATE = """
You are PromptBoost, a highly structured AI assistant. Your task is to take a user's vague prompt and break it down into key components and questions that need to be answered to create a high-quality final prompt.

RULES:
- Identify the core goal of the user's prompt.
- List 3-5 critical aspects, questions, or details the user should include.
- Format the output clearly, using markdown for lists.
- Do NOT answer the prompt. Only deconstruct it into a better prompt.
- The output MUST be only the enhanced prompt, with no preamble.

VAGUE USER PROMPT: {user_prompt}
ENHANCED PROMPT (breakdown format):"""


# --- 2. INITIALIZE THE LLM PROVIDERS (WITH CORRECTED VALUES) ---

try:
    groq_chat = ChatGroq(
        temperature=1.7,
        groq_api_key=settings.GROQ_API_KEY,
        # Using a faster, more reliable model for this task
        model_name="llama3-8b-8192"
    )

    gemini_chat = ChatGoogleGenerativeAI(
        # Using the newer, faster Flash model
        model="gemini-1.5-flash-latest",
        google_api_key=settings.GOOGLE_API_KEY,
        # CORRECTED: Temperature must be between 0.0 and 1.0
        temperature=1.7
    )
    logger.info("Successfully initialized both Groq and Gemini models.")

except Exception as e:
    logger.error(f"CRITICAL: Failed to initialize LLMs. Check API keys and model names: {e}")
    groq_chat = None
    gemini_chat = None

# --- 3. CREATE THE CORE ENHANCEMENT FUNCTIONS ---

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