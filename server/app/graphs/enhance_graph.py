from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from app.crud import prompt_cache as crud
from app.schemas import prompt as schemas
from sqlalchemy.orm import Session
from app.services import llm_service # <-- IMPORT OUR NEW SERVICE

# --- 1. Define the State ---
class GraphState(TypedDict):
    original_prompt: str
    enhanced_prompt: str | None
    from_cache: bool
    db: Session

# --- 2. Define the Nodes ---

def check_cache(state: GraphState):
    """Checks if the prompt exists in the PostgreSQL cache."""
    print("---NODE: CHECK CACHE---")
    db = state["db"]
    original_prompt = state["original_prompt"]
    cached_result = crud.get_prompt_by_original_text(db, original_prompt)
    
    if cached_result:
        print("---CACHE HIT---")
        return {
            "from_cache": True,
            "enhanced_prompt": cached_result.enhanced_prompt
        }
    else:
        print("---CACHE MISS---")
        return { "from_cache": False }

# --- THIS IS THE UPDATED NODE ---
def enhance_with_llm(state: GraphState):
    """
    Calls the external LLM service to get the enhanced prompt.
    Replaces the old placeholder logic.
    """
    print("---NODE: ENHANCE WITH LLM (REAL CALL)---")
    original_prompt = state["original_prompt"]

    # Call the function from our new service
    enhanced_version = llm_service.get_enhanced_prompt(original_prompt)

    # Handle the edge case where both Groq and Gemini fail
    if not enhanced_version:
        print("---ERROR: LLM enhancement failed after all fallbacks.---")
        # We should still provide a valid string to avoid downstream errors
        enhanced_version = f"{original_prompt}\n\n[// Enhancement failed on server, please try again.]"

    return {"enhanced_prompt": enhanced_version}


def save_to_cache(state: GraphState):
    """Saves the newly enhanced prompt to the cache."""
    print("---NODE: SAVE TO CACHE---")
    db = state["db"]
    original_prompt = state["original_prompt"]
    enhanced_prompt = state["enhanced_prompt"]

    if original_prompt and enhanced_prompt:
        prompt_data_to_save = schemas.PromptCacheCreate(
            original_prompt=original_prompt,
            enhanced_prompt=enhanced_prompt
        )
        crud.create_cached_prompt(db, prompt=prompt_data_to_save)
    return {}

# --- 3. Define the Edges ---
def decide_to_enhance(state: GraphState) -> Literal["enhance_with_llm", "__end__"]:
    """Conditional edge. If the prompt was found in the cache, we finish."""
    print("---EDGE: DECIDING NEXT STEP---")
    if state["from_cache"]:
        print("---DECISION: END---")
        return END
    else:
        print("---DECISION: ENHANCE---")
        return "enhance_with_llm"

# --- 4. Build and Compile the Graph ---
def create_enhancement_graph():
    workflow = StateGraph(GraphState)
    workflow.add_node("check_cache", check_cache)
    workflow.add_node("enhance_with_llm", enhance_with_llm)
    workflow.add_node("save_to_cache", save_to_cache)
    workflow.set_entry_point("check_cache")
    workflow.add_edge("enhance_with_llm", "save_to_cache")
    workflow.add_edge("save_to_cache", END)
    workflow.add_conditional_edges("check_cache", decide_to_enhance)
    return workflow.compile()

enhancement_graph = create_enhancement_graph()