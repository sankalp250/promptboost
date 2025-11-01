import uuid
from typing import TypedDict
from langgraph.graph import StateGraph, END
from app.crud import prompt_cache as crud
from app.schemas import prompt as schemas
from sqlalchemy.orm import Session
from app.services import llm_service

# --- 1. SIMPLIFIED STATE ---
# We no longer need experiment_group or enhancement_strategy in the active state.
class GraphState(TypedDict):
    original_prompt: str
    enhanced_prompt: str | None
    from_cache: bool
    db: Session
    user_id: uuid.UUID
    session_id: uuid.UUID
    prompt_id: int | None

# --- 2. SIMPLIFIED NODES ---

def check_cache(state: GraphState):
    """Checks the cache."""
    print("---NODE: CHECK CACHE---")
    cached = crud.get_prompt_by_original_text(state["db"], state["original_prompt"])
    if cached:
        print("---CACHE HIT---")
        return {"from_cache": True, "enhanced_prompt": cached.enhanced_prompt}
    else:
        print("---CACHE MISS---")
        return {"from_cache": False}

def enhance_prompt(state: GraphState):
    """Calls the single, unified enhancement service."""
    print("---NODE: ENHANCE PROMPT---")
    enhanced = llm_service.get_enhanced_prompt(state["original_prompt"])
    return {"enhanced_prompt": enhanced}

# ... (all other code in the file is correct) ...

def save_results(state: GraphState):
    """Saves the prompt and analytics, now with 'accepted' as the default action."""
    print("---NODE: SAVE RESULTS---")
    db = state["db"]
    enhanced_prompt = state["enhanced_prompt"]

    if enhanced_prompt is None:
        print("---WARNING: Enhancement failed. Skipping DB save.---")
        return {}

    prompt_to_cache = schemas.PromptCacheCreate(
        original_prompt=state["original_prompt"],
        enhanced_prompt=enhanced_prompt
    )
    created_prompt_obj = crud.create_cached_prompt(db, prompt=prompt_to_cache)
    prompt_id = created_prompt_obj.id

    if prompt_id:
        analytics_to_save = schemas.UsageAnalyticsCreate(
            prompt_id=prompt_id,
            user_id=state["user_id"],
            session_id=state["session_id"],
            enhancement_strategy="engineer_v1",
            # --- THE FIX IS HERE ---
            # Set the default user_action to 'accepted'.
            user_action="accepted"
        )
        crud.create_usage_analytics_entry(db, analytics_data=analytics_to_save)
    
    return {"prompt_id": prompt_id}

# ... (the rest of the graph build is correct) ...


# --- 3. BUILD THE NEW, LINEAR GRAPH ---
workflow = StateGraph(GraphState)

workflow.add_node("check_cache", check_cache)
workflow.add_node("enhance_prompt", enhance_prompt)
workflow.add_node("save_results", save_results)

# A simple edge function to decide the next step
def decide_next_step(state: GraphState):
    return "enhance_prompt" if not state["from_cache"] else END

workflow.set_entry_point("check_cache")
workflow.add_conditional_edges("check_cache", decide_next_step)
workflow.add_edge("enhance_prompt", "save_results")
workflow.add_edge("save_results", END)

enhancement_graph = workflow.compile()