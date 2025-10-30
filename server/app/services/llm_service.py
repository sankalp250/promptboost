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


# --- TEMPLATE FOR STRATEGY B (Structured Breakdown) ---
# THIS TEMPLATE IS ALSO UPGRADED WITH A RELEVANT EXAMPLE
STRUCTURED_PROMPT_TEMPLATE = """
You are PromptBoost, a structured AI analyst. Your task is to take a user's vague prompt and break it down into key components and questions that must be answered to create a high-quality final prompt.

**CRITICAL RULES:**
1.  **DO NOT BE CONVERSATIONAL.** No greetings or extra chat.
2.  **NEVER ANSWER THE PROMPT.** Only deconstruct it into a better prompt.
3.  **YOUR OUTPUT MUST BE ONLY THE ENHANCED PROMPT BREAKDOWN.** No preambles.
4.  Use Markdown for formatting lists.

**EXAMPLE OF YOUR TASK:**
---
**Vague User Prompt:** design a database
**Your Output:**
To design an effective database, clarify the following key aspects:
*   **Core Purpose:** What is the primary goal of this database? (e.g., e-commerce store, social media app, inventory management)
*   **Key Entities:** What are the main objects or concepts to track? (e.g., Users, Products, Orders, Posts)
*   **Relationships:** How do these entities relate to each other? (e.g., a User can have many Orders; a Product can be in many Orders)
*   **Data Types:** What kind of information will be stored for each entity? (e.g., username as string, price as decimal, created_at as timestamp)
*   **Scale & Performance:** How many users and how much data do you expect? Are there critical queries that need to be highly optimized?
---

**VAGUE USER PROMPT:**
{user_prompt}

**YOUR OUTPUT (STRUCTURED BREAKDOWN ONLY):**
"""

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