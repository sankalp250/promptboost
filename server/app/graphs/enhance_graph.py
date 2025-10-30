import uuid
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from app.crud import prompt_cache as crud
from app.schemas import prompt as schemas
from sqlalchemy.orm import Session
from app.services import llm_service

# --- 1. STATE DEFINITION (Unchanged) ---
class GraphState(TypedDict):
    original_prompt: str
    enhanced_prompt: str | None
    from_cache: bool
    db: Session
    user_id: uuid.UUID
    session_id: uuid.UUID
    prompt_id: int | None
    experiment_group: Literal["A", "B"] | None
    enhancement_strategy: str | None

# --- 2. GRAPH NODES ---

def check_cache(state: GraphState):
    """Checks the cache. Same as before."""
    print("---NODE: CHECK CACHE---")
    cached = crud.get_prompt_by_original_text(state["db"], state["original_prompt"])
    if cached:
        print("---CACHE HIT---")
        return {"from_cache": True, "enhanced_prompt": cached.enhanced_prompt}
    else:
        print("---CACHE MISS---")
        return {"from_cache": False}

def assign_experiment_group(state: GraphState):
    """Assigns user to Group A or B based on their user_id."""
    print("---NODE: ASSIGN EXPERIMENT GROUP---")
    group = "A" if int(state["user_id"].hex, 16) % 2 == 0 else "B"
    print(f"User {state['user_id']} assigned to Group {group}")
    return {"experiment_group": group}

def enhance_strategy_A(state: GraphState):
    """Enhancement strategy for Group A (standard)."""
    print("---NODE: ENHANCE STRATEGY A (standard)---")
    enhanced = llm_service.get_enhanced_prompt_strategy_A(state["original_prompt"])
    return {"enhanced_prompt": enhanced, "enhancement_strategy": "standard_v1"}

def enhance_strategy_B(state: GraphState):
    """Enhancement strategy for Group B (alternative)."""
    print("---NODE: ENHANCE STRATEGY B (structured)---")
    enhanced = llm_service.get_enhanced_prompt_strategy_B(state["original_prompt"])
    return {"enhanced_prompt": enhanced, "enhancement_strategy": "structured_v1"}

# --- UPDATED AND ROBUST 'save_results' NODE ---
def save_results(state: GraphState):
    """
    Saves the prompt cache and analytics entry, now robust to enhancement failures.
    """
    print("---NODE: SAVE RESULTS---")
    db = state["db"]
    enhanced_prompt = state["enhanced_prompt"]

    # --- THE CRUCIAL FIX IS HERE ---
    # Check if the enhancement succeeded (is not None) before trying to save.
    if enhanced_prompt is None:
        print("---WARNING: Enhancement failed, LLM service returned None. Skipping database save.---")
        # Return an empty dictionary to allow the graph to finish gracefully.
        return {}

    # This code below will now only run if the enhancement was successful.
    if not state["from_cache"]:
        prompt_to_cache = schemas.PromptCacheCreate(
            original_prompt=state["original_prompt"],
            enhanced_prompt=enhanced_prompt  # Use the validated variable
        )
        created_prompt_obj = crud.create_cached_prompt(db, prompt=prompt_to_cache)
        prompt_id = created_prompt_obj.id
    else:
        cached_prompt = crud.get_prompt_by_original_text(db, state["original_prompt"])
        prompt_id = cached_prompt.id if cached_prompt else None

    # Save the detailed analytics entry
    if prompt_id:
        analytics_to_save = schemas.UsageAnalyticsCreate(
            prompt_id=prompt_id,
            user_id=state["user_id"],
            session_id=state["session_id"],
            experiment_group=state["experiment_group"],
            enhancement_strategy=state["enhancement_strategy"]
        )
        crud.create_usage_analytics_entry(db, analytics_data=analytics_to_save)

    return {"prompt_id": prompt_id}


# --- 3. CONDITIONAL EDGES (Unchanged) ---

def route_after_cache_check(state: GraphState) -> Literal["save_results", "assign_experiment_group"]:
    """If cache hit, save analytics. If miss, run the A/B test."""
    if state["from_cache"]:
        return "save_results"
    else:
        return "assign_experiment_group"

def route_to_strategy(state: GraphState) -> Literal["enhance_strategy_A", "enhance_strategy_B"]:
    """Routes to the correct enhancement node based on the assigned group."""
    if state["experiment_group"] == "A":
        return "enhance_strategy_A"
    else:
        return "enhance_strategy_B"

# --- 4. GRAPH CONSTRUCTION (Unchanged) ---

workflow = StateGraph(GraphState)

workflow.add_node("check_cache", check_cache)
workflow.add_node("assign_experiment_group", assign_experiment_group)
workflow.add_node("enhance_strategy_A", enhance_strategy_A)
workflow.add_node("enhance_strategy_B", enhance_strategy_B)
workflow.add_node("save_results", save_results)

workflow.set_entry_point("check_cache")
workflow.add_conditional_edges(
    "check_cache",
    route_after_cache_check,
    {"save_results": END, "assign_experiment_group": "assign_experiment_group"}
)
workflow.add_conditional_edges(
    "assign_experiment_group",
    route_to_strategy,
    {"enhance_strategy_A": "enhance_strategy_A", "enhance_strategy_B": "enhance_strategy_B"}
)
workflow.add_edge("enhance_strategy_A", "save_results")
workflow.add_edge("enhance_strategy_B", "save_results")

enhancement_graph = workflow.compile()