import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 1. DEFINE PROMPT TEMPLATES ---
# We'll start with a generic one, but you can add more specialized ones later
GENERIC_PROMPT_TEMPLATE = """
You are PromptBoost, a world-class AI assistant specialized in enhancing user prompts.
Your goal is to take a user's vague idea and transform it into a clear, detailed, and effective prompt for another AI.
Do NOT answer the prompt directly. Instead, rewrite it to be better.

RULES:
- Add specific details and context.
- Suggest a format if appropriate (e.g., "in a JSON format").
- Incorporate best practices like asking the AI to "think step-by-step".
- The output MUST be only the enhanced prompt, with no preamble or explanation.

VAGUE USER PROMPT:
{user_prompt}

ENHANCED PROMPT:
"""
# --- NEW: TEMPLATE FOR STRATEGY B ---
STRUCTURED_PROMPT_TEMPLATE = """
You are PromptBoost, a highly structured AI assistant.
Your task is to take a user's vague prompt and break it down into key components and questions that need to be answered to create a high-quality final prompt.

RULES:
- Identify the core goal of the user's prompt.
- List 3-5 critical aspects, questions, or details the user should include.
- Format the output clearly, using markdown for lists.
- Do NOT answer the prompt. Only deconstruct it into a better prompt.
- The output MUST be only the enhanced prompt, with no preamble.

VAGUE USER PROMPT:
{user_prompt}

ENHANCED PROMPT (breakdown format):
"""

# --- 2. INITIALIZE THE LLM PROVIDERS ---

try:
    # Primary, fast LLM
    groq_chat = ChatGroq(
        temperature=1.7,
        groq_api_key=settings.GROQ_API_KEY,
        model_name="llama3-70b-8192"
    )

    # Backup, reliable LLM
    gemini_chat = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=1.7
    )

    # Set up a generic LangChain "chain" for prompt enhancement
    prompt_enhancement_chain = (
        ChatPromptTemplate.from_template(GENERIC_PROMPT_TEMPLATE)
        | StrOutputParser()
    )

except Exception as e:
    logger.error(f"Failed to initialize LLMs. Check API keys and dependencies: {e}")
    groq_chat = None
    gemini_chat = None

# --- 3. CREATE THE CORE ENHANCEMENT FUNCTIONS ---

def get_enhanced_prompt(user_prompt: str) -> str | None:
    """Legacy enhancement using the generic chain (kept for backward compatibility)."""
    if not groq_chat or not gemini_chat:
        logger.error("LLM services are not available.")
        return "**Enhanced by LLM:** A critical configuration error occurred on the server."

    try:
        logger.info(f"Attempting enhancement with primary LLM (Groq) for: '{user_prompt}'")
        chain = prompt_enhancement_chain | groq_chat
        enhanced_prompt = chain.invoke({"user_prompt": user_prompt})
        logger.info("Successfully enhanced with Groq.")
        return enhanced_prompt
    except Exception as e:
        logger.warning(f"Primary LLM (Groq) failed: {e}. Falling back to secondary LLM (Gemini).")
        try:
            chain = prompt_enhancement_chain | gemini_chat
            enhanced_prompt = chain.invoke({"user_prompt": user_prompt})
            logger.info("Successfully enhanced with Gemini.")
            return enhanced_prompt
        except Exception as e2:
            logger.error(f"Secondary LLM (Gemini) also failed: {e2}")
            return None


def get_enhanced_prompt_strategy_A(user_prompt: str) -> str | None:
    """Enhances using the generic, free-form strategy."""
    if not groq_chat or not gemini_chat:
        return "Server configuration error."

    try:
        chain = ChatPromptTemplate.from_template(GENERIC_PROMPT_TEMPLATE) | groq_chat | StrOutputParser()
        return chain.invoke({"user_prompt": user_prompt})
    except Exception:
        chain = ChatPromptTemplate.from_template(GENERIC_PROMPT_TEMPLATE) | gemini_chat | StrOutputParser()
        return chain.invoke({"user_prompt": user_prompt})


def get_enhanced_prompt_strategy_B(user_prompt: str) -> str | None:
    """Enhances using a more structured, breakdown-focused strategy."""
    if not groq_chat or not gemini_chat:
        return "Server configuration error."

    try:
        chain = ChatPromptTemplate.from_template(STRUCTURED_PROMPT_TEMPLATE) | groq_chat | StrOutputParser()
        return chain.invoke({"user_prompt": user_prompt})
    except Exception:
        chain = ChatPromptTemplate.from_template(STRUCTURED_PROMPT_TEMPLATE) | gemini_chat | StrOutputParser()
        return chain.invoke({"user_prompt": user_prompt})