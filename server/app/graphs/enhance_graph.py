import uuid
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from app.crud import prompt_cache as crud
from app.schemas import prompt as schemas
from sqlalchemy.orm import Session
from app.services import llm_service

# --- 1. EXPAND THE STATE ---
# The state now holds all the information for our experiment.
class GraphState(TypedDict):
    original_prompt: str
    enhanced_prompt: str | None
    from_cache: bool
    db: Session
    # New analytics fields
    user_id: uuid.UUID
    session_id: uuid.UUID
    prompt_id: int | None # Will be set after saving the prompt
    experiment_group: Literal["A", "B"] | None
    enhancement_strategy: str | None

# --- 2. DEFINE THE NEW AND UPDATED NODES ---

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
    # A simple, deterministic way to split users into two groups
    group = "A" if int(state["user_id"].hex, 16) % 2 == 0 else "B"
    print(f"User {state['user_id']} assigned to Group {group}")
    return {"experiment_group": group}

def enhance_strategy_A(state: GraphState):
    """Enhancement strategy for Group A (standard)."""
    print("---NODE: ENHANCE STRATEGY A (standard)---")
    enhanced = llm_service.get_enhanced_prompt(state["original_prompt"])
    return {"enhanced_prompt": enhanced, "enhancement_strategy": "standard_v1"}

def enhance_strategy_B(state: GraphState):
    """Enhancement strategy for Group B (alternative)."""
    print("---NODE: ENHANCE STRATEGY B (alternative)---")
    # For now, we'll just use a placeholder to prove the logic works.
    # In the future, you could call a different LLM or use a different prompt template here.
    enhanced = f"**Alternative Strategy B:** Consider the following aspects for '{state['original_prompt']}': [Aspect 1], [Aspect 2]."
    return {"enhanced_prompt": enhanced, "enhancement_strategy": "alternative_v1"}

def save_results(state: GraphState):
    """Saves both the prompt cache and the detailed analytics entry."""
    print("---NODE: SAVE RESULTS---")
    db = state["db"]
    # We only save to prompt_cache if it was a miss
    if not state["from_cache"]:
        prompt_to_cache = schemas.PromptCacheCreate(
            original_prompt=state["original_prompt"],
            enhanced_prompt=state["enhanced_prompt"]
        )
        # We get the newly created prompt object back, which has the ID we need
        created_prompt_obj = crud.create_cached_prompt(db, prompt=prompt_to_cache)
        prompt_id = created_prompt_obj.id
    else:
        # If it was a cache hit, we need to find the ID
        cached_prompt = crud.get_prompt_by_original_text(db, state["original_prompt"])
        prompt_id = cached_prompt.id if cached_prompt else None
    
    # Now, save the detailed analytics entry
    if prompt_id:
        analytics_to_save = schemas.UsageAnalyticsCreate(
            prompt_id=prompt_id,
            user_id=state["user_id"],
            session_id=state["session_id"],
            experiment_group=state["experiment_group"],
            enhancement_strategy=state["enhancement_strategy"]
            # user_action will be set later via the /feedback endpoint
        )
        crud.create_usage_analytics_entry(db, analytics_data=analytics_to_save)
    return {"prompt_id": prompt_id}


# --- 3. DEFINE THE NEW CONDITIONAL EDGES ---

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

# --- 4. BUILD THE NEW GRAPH ---

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