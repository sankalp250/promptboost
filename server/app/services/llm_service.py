import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import settings
import logging
import re # Import the regular expression library

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- HELPER FUNCTION TO DETECT CONTEXT ---
def detect_context(user_prompt):
    """A simple helper to detect programming languages and add context."""
    context_str = ""
    # Use case-insensitive regex to find common languages
    if re.search(r'\b(python|pytest|fastapi)\b', user_prompt, re.IGNORECASE):
        return "Act as a Senior Python Developer specializing in Test-Driven Development and FastAPI."
    if re.search(r'\b(javascript|react|js|node)\b', user_prompt, re.IGNORECASE):
        return "Act as a Full-Stack JavaScript Developer experienced with the MERN stack."
    if re.search(r'\b(stripe|payment)\b', user_prompt, re.IGNORECASE):
        return "Act as a Senior Backend Engineer experienced with e-commerce payment gateways."
    # Default persona if no specific context is found
    return "Act as a Senior Software Engineer and AI expert."

# --- THE NEW, CONTEXT-AWARE TEMPLATE ---
ENHANCEMENT_PROMPT_TEMPLATE = """
**Persona:** {persona}

**User's Vague Prompt:**
{user_prompt}

**Your Task:**
Rewrite the user's vague prompt into a detailed, professional, and actionable request for an AI model.

**CRITICAL RULES:**
1.  **Embody the Persona:** Use the language and mindset of the assigned persona.
2.  **Add Specificity:** Infer the user's needs and add technical details (libraries, function names, API endpoints, file names) that would be expected in a professional context.
3.  **Provide Structure:** Use clear formatting like lists or code blocks where appropriate.
4.  **DO NOT BE CONVERSATIONAL.** No greetings or chitchat.
5.  **YOUR OUTPUT MUST BE ONLY THE FINAL, ENHANCED PROMPT.** No other text.
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
    """Enhances a prompt using context detection and a persona-based template."""
    if not groq_chat or not gemini_chat:
        return "Server configuration error."
    
    # 1. Detect the context and select a persona
    persona = detect_context(user_prompt)
    logger.info(f"Detected persona: {persona}")
    
    # 2. Set up the LangChain chain with the template
    prompt_template = ChatPromptTemplate.from_template(ENHANCEMENT_PROMPT_TEMPLATE)

    # 3. Invoke the chain with fallback logic
    try:
        logger.info(f"Attempting enhancement with Groq...")
        chain = prompt_template | groq_chat | StrOutputParser()
        return chain.invoke({"user_prompt": user_prompt, "persona": persona})
    except Exception as e:
        logger.warning(f"Groq failed: {e}. Falling back to Gemini.")
        try:
            chain = prompt_template | gemini_chat | StrOutputParser()
            return chain.invoke({"user_prompt": user_prompt, "persona": persona})
        except Exception as e2:
            logger.error(f"Gemini fallback also failed: {e2}")
            return None