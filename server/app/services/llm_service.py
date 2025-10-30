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

# --- 2. INITIALIZE THE LLM PROVIDERS ---

try:
    # Primary, fast LLM
    groq_chat = ChatGroq(
        temperature=0.7,
        groq_api_key=settings.GROQ_API_key,
        model_name="llama3-70b-8192"
    )

    # Backup, reliable LLM
    gemini_chat = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.7
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

# --- 3. CREATE THE CORE ENHANCEMENT FUNCTION ---

def get_enhanced_prompt(user_prompt: str) -> str | None:
    """
    Enhances a user prompt using a primary LLM (Groq) with a fallback to a secondary (Gemini).
    """
    if not groq_chat or not gemini_chat:
        logger.error("LLM services are not available.")
        return "**Enhanced by LLM:** A critical configuration error occurred on the server."

    try:
        logger.info(f"Attempting enhancement with primary LLM (Groq) for: '{user_prompt}'")
        # Combine the chain with the Groq model
        chain = prompt_enhancement_chain | groq_chat
        enhanced_prompt = chain.invoke({"user_prompt": user_prompt})
        logger.info("Successfully enhanced with Groq.")
        return enhanced_prompt

    except Exception as e:
        logger.warning(f"Primary LLM (Groq) failed: {e}. Falling back to secondary LLM (Gemini).")
        try:
            # Combine the chain with the Gemini model as a fallback
            chain = prompt_enhancement_chain | gemini_chat
            enhanced_prompt = chain.invoke({"user_prompt": user_prompt})
            logger.info("Successfully enhanced with Gemini.")
            return enhanced_prompt
        
        except Exception as e2:
            logger.error(f"Secondary LLM (Gemini) also failed: {e2}")
            return None # Return None if both fail