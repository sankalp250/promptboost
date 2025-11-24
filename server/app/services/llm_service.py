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

IMAGE_KEYWORDS = [
    "image", "photo", "photograph", "picture", "render", "midjourney",
    "stable diffusion", "dall", "ideogram", "illustration", "concept art",
    "digital art", "artwork", "portrait", "landscape", "cinematic still",
    "poster", "cover art", "oil painting", "watercolor", "3d render",
    "anime", "pixel art", "sculpture", "studio shot", "macro shot",
    "ultra realistic", "hdr", "4k", "8k"
]

def is_image_prompt(user_prompt: str) -> bool:
    """Heuristically determine if the user is asking for an image-generation prompt."""
    if not user_prompt:
        return False
    lowered = user_prompt.lower()
    return any(keyword in lowered for keyword in IMAGE_KEYWORDS)

def is_code(user_prompt):
    """Detects if the user input is likely raw code and should not be enhanced."""
    code_indicators = [
        r'^import\s+', r'^from\s+\w+\s+import', r'^def\s+\w+\s*\(', r'^class\s+\w+',
        r'^\s*assert\s', r'^\s*@', r'^\s*if\s+.*:', r'^\s*return\s', r'^\s*async\s+def',
    ]
    lines = user_prompt.strip().split('\n')
    if len(lines) > 3 and any(line.startswith(('    ', '\t')) for line in lines[1:]):
        return True
    code_line_count = 0
    for line in lines[:10]:
        for pattern in code_indicators:
            if re.search(pattern, line.strip()):
                code_line_count += 1
                break
    return code_line_count >= 2

def detect_context(user_prompt):
    """Detects programming or creative context to assign a persona."""
    if is_image_prompt(user_prompt):
        return (
            "Act as an award-winning visual prompt designer for Midjourney, "
            "Stable Diffusion, DALL·E, Ideogram, and other generative image models."
        )
    if re.search(r'\b(python|pytest|fastapi|py)\b', user_prompt, re.IGNORECASE):
        return "Act as a Senior Python Developer specializing in Test-Driven Development and FastAPI."
    if re.search(r'\b(javascript|react|js|node|typescript|ts)\b', user_prompt, re.IGNORECASE):
        return "Act as a Full-Stack JavaScript Developer experienced with the MERN stack and TypeScript."
    if re.search(r'\b(stripe|payment|charge|checkout)\b', user_prompt, re.IGNORECASE):
        return "Act as a Senior Backend Engineer experienced with e-commerce payment gateways."
    return "Act as a Senior Software Engineer and AI expert."

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

IMAGE_PROMPT_TEMPLATE = """
<INSTRUCTIONS>
You are an elite visual prompt designer. Your job is to transform the user's idea into a cinematic, production-ready image prompt that can be pasted directly into Midjourney, Stable Diffusion, DALL·E, Ideogram, or any generative image model.

<RULES>
- Study the <user_prompt> to understand the subject, environment, composition, camera details or art medium, mood, lighting, color palette, and any storytelling cues.
- Enrich the idea with evocative but concise language: concrete nouns + precise adjectives.
- Include cinematic or photographic guidance when applicable (lens, aperture, camera angle) OR artistic medium (oil painting, watercolor, 3D render, anime cel, etc.).
- Reference lighting, color palette, mood, and texture so the model understands the vibe.
- Mention quality modifiers only when useful (e.g., "ultra-detailed", "8k", "octane render", "film grain").
- The final output MUST be a single paragraph with no headings, no lists, and no XML tags.
- Do NOT add prefixes like "Prompt:". Output ONLY the enhanced image prompt.
</RULES>

<EXAMPLE>
<user_prompt>a futuristic city at night</user_prompt>
<ENHANCED_PROMPT>
Neon-soaked futuristic megacity at midnight, towering arcology skylines wrapped in holographic billboards, rain-slick streets reflecting cyan and magenta light, cinematic wide-angle shot from a low street perspective, volumetric fog, flying traffic streaks, ultra-detailed, 8k, inspired by Syd Mead concept art.
</ENHANCED_PROMPT>
</EXAMPLE>

<TASK>
<persona>{persona}</persona>
<user_prompt>{user_prompt}</user_prompt>
<ENHANCED_PROMPT>
</ENHANCED_PROMPT>
</TASK>
"""

REROLL_INSTRUCTION = """
<CRITICAL_REROLL_INSTRUCTION>
⚠️ THE USER REJECTED THE PREVIOUS ENHANCEMENT AND REQUESTED A COMPLETELY DIFFERENT ONE. ⚠️

The previous enhancement (REJECTED) was:
{previous_enhancement}

Produce a DISTINCTLY DIFFERENT enhancement that:
1. Uses different wording and structure
2. Approaches the concept from a new perspective
3. Introduces novel details, tone, or composition ideas
4. Avoids repeating the rejected version
</CRITICAL_REROLL_INSTRUCTION>
"""

try:
    # Groq is now primary LLM
    primary_llm = ChatGroq(
        temperature=0.7,
        groq_api_key=settings.GROQ_API_KEY,
        model_name="llama-3.1-8b-instant"
    )
    # Gemini as optional fallback (will be None if API key is invalid)
    try:
        fallback_llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.7
        )
        logger.info("Successfully initialized Groq (Primary) and Gemini (Fallback) models.")
    except Exception as gemini_error:
        logger.warning(f"Gemini fallback initialization failed (will use Groq only): {gemini_error}")
        fallback_llm = None
        logger.info("Successfully initialized Groq (Primary) - Gemini fallback unavailable.")
except Exception as e:
    logger.error(f"CRITICAL: Failed to initialize primary LLM (Groq): {e}")
    primary_llm = None
    fallback_llm = None

def clean_llm_output(raw_output: str) -> str:
    """Extract and clean the enhanced prompt from LLM output, removing XML tags and extra formatting."""
    if not raw_output:
        return raw_output
    
    output = raw_output.strip()
    
    # Extract content from <ENHANCED_PROMPT> tags if present
    enhanced_match = re.search(r'<ENHANCED_PROMPT>(.*?)</ENHANCED_PROMPT>', output, re.DOTALL | re.IGNORECASE)
    if enhanced_match:
        output = enhanced_match.group(1).strip()
    
    # Remove all XML tags
    output = re.sub(r'<[^>]+>', '', output)
    
    # Remove common prefixes that LLMs sometimes add
    prefixes_to_remove = [
        r'^Enhanced prompt:.*?\n',
        r'^Enhanced Prompt:.*?\n',
        r'^Here is.*?:.*?\n',
        r'^Here.*?enhanced.*?:.*?\n',
        r'^\*\*.*?:\*\*.*?\n',
        r'^Task Request:.*?\n',
        r'^Project Context:.*?\n',
    ]
    
    for pattern in prefixes_to_remove:
        output = re.sub(pattern, '', output, flags=re.IGNORECASE | re.MULTILINE)
    
    # Remove markdown task description blocks
    lines = output.split('\n')
    cleaned_lines = []
    skip_until_content = True
    
    for line in lines:
        line_lower = line.lower().strip()
        # Skip task description headers
        if any(keyword in line_lower for keyword in ['task request', 'project context', 'specific requirements', 'deliverables', 'acceptance criteria', '**task']):
            skip_until_content = True
            continue
        
        # If we hit actual content (not empty, not a header), start collecting
        if line.strip() and not line.strip().startswith('**') and not line_lower.startswith(('task:', 'request:', 'deliverable', 'acceptance')):
            skip_until_content = False
        
        if not skip_until_content:
            cleaned_lines.append(line)
    
    cleaned = '\n'.join(cleaned_lines).strip()
    
    # Fallback: if cleaned is empty or too short, return original output with basic cleaning
    if not cleaned or len(cleaned) < 20:
        cleaned = re.sub(r'<[^>]+>', '', output).strip()
    
    return cleaned

def get_enhanced_prompt(user_prompt: str, is_reroll: bool = False, previous_enhancement: str | None = None) -> str | None:
    if not primary_llm:
        return "Server configuration error: Primary LLM (Groq) not initialized."
    
    persona = detect_context(user_prompt)
    prompt_is_image = is_image_prompt(user_prompt)
    logger.info(f"Detected persona: {persona}")
    logger.info("Detected image prompt" if prompt_is_image else "Detected text/code prompt")
    
    prompt_body = IMAGE_PROMPT_TEMPLATE if prompt_is_image else ENHANCEMENT_PROMPT_TEMPLATE
    
    # Modify template for rerolls
    if is_reroll and previous_enhancement:
        prompt_body = prompt_body + REROLL_INSTRUCTION
        prompt_template = ChatPromptTemplate.from_template(prompt_body)
        template_vars = {
            "user_prompt": user_prompt,
            "persona": persona,
            "previous_enhancement": previous_enhancement,
        }
    else:
        prompt_template = ChatPromptTemplate.from_template(prompt_body)
        template_vars = {"user_prompt": user_prompt, "persona": persona}

    try:
        logger.info(f"Attempting enhancement with Primary LLM (Groq)... {'(REROLL)' if is_reroll else ''}")
        # Use higher temperature for rerolls to encourage more variation
        llm_to_use = primary_llm
        if is_reroll:
            # Create a new LLM instance with higher temperature for rerolls
            llm_to_use = ChatGroq(
                temperature=1.0,  # Higher temperature for more variation in rerolls
                groq_api_key=settings.GROQ_API_KEY,
                model_name="llama-3.1-8b-instant"
            )
        chain = prompt_template | llm_to_use | StrOutputParser()
        raw_output = chain.invoke(template_vars)
        cleaned = clean_llm_output(raw_output)
        logger.info(f"Raw output length: {len(raw_output)}, Cleaned length: {len(cleaned)}")
        return cleaned
    except Exception as e:
        logger.warning(f"Primary LLM (Groq) failed: {e}.")
        # Try fallback if available
        if fallback_llm:
            try:
                logger.info(f"Attempting fallback with Gemini... {'(REROLL)' if is_reroll else ''}")
                # Use higher temperature for rerolls
                fallback_llm_to_use = fallback_llm
                if is_reroll:
                    fallback_llm_to_use = ChatGoogleGenerativeAI(
                        model="gemini-1.5-flash-latest",
                        google_api_key=settings.GOOGLE_API_KEY,
                        temperature=0.9  # Higher temperature for rerolls
                    )
                chain = prompt_template | fallback_llm_to_use | StrOutputParser()
                raw_output = chain.invoke(template_vars)
                cleaned = clean_llm_output(raw_output)
                logger.info(f"Raw output length: {len(raw_output)}, Cleaned length: {len(cleaned)}")
                return cleaned
            except Exception as e2:
                logger.error(f"Fallback LLM (Gemini) also failed: {e2}")
                return "Error: All LLM services failed. Please check API keys and model availability."
        else:
            logger.error(f"No fallback LLM available. Groq error: {e}")
            return f"Error: Primary LLM (Groq) failed: {str(e)}"