import uuid
from typing import TypedDict
from langgraph.graph import StateGraph, END
from app.crud import prompt_cache as crud
from app.schemas import prompt as schemas
from sqlalchemy.orm import Session
from app.services import llm_service, ml_inference_service

class GraphState(TypedDict):
    original_prompt: str
    enhanced_prompt: str | None
    from_cache: bool
    db: Session
    user_id: uuid.UUID
    session_id: uuid.UUID
    prompt_id: int | None
    is_reroll: bool
    previous_enhancement: str | None
    quality_score: float | None
    retry_count: int | None
    project_id: str | None
    recent_prompts: list[tuple[str, str]] | None  # (original, enhanced) for continuity
    project_context: str | None

def check_cache(state: GraphState):
    print("---NODE: CHECK CACHE---")
    if llm_service.is_code(state["original_prompt"]):
        print("Input is raw code. Bypassing enhancement.")
        return {"from_cache": False, "enhanced_prompt": state["original_prompt"]}
    
    # TEMPORARILY DISABLED FOR DATA COLLECTION
    # Always return cache miss to force new enhancements
    print("---CACHE DISABLED FOR DATA COLLECTION (forcing cache miss)---")
    return {"from_cache": False}
    
    # Original cache logic (commented out temporarily)
    # cached = crud.get_prompt_by_original_text(state["db"], state["original_prompt"])
    # if cached:
    #     print("---CACHE HIT---")
    #     analytics_to_save = schemas.UsageAnalyticsCreate(
    #         prompt_id=cached.id,
    #         user_id=state["user_id"],
    #         session_id=state["session_id"],
    #         enhancement_strategy="engineer_v3_groq_primary",
    #         user_action="accepted"
    #     )
    #     crud.create_usage_analytics_entry(state["db"], analytics_data=analytics_to_save)
    #     print("---CREATED NEW ANALYTICS ENTRY FOR CACHED PROMPT---")
    #     return {"from_cache": True, "enhanced_prompt": cached.enhanced_prompt}
    # else:
    #     print("---CACHE MISS---")
    #     return {"from_cache": False}

def enhance_prompt(state: GraphState):
    print("---NODE: ENHANCE PROMPT---")
    retry_count = (state.get("retry_count", 0) or 0) + 1
    recent = state.get("recent_prompts") or []
    project_ctx = state.get("project_context") or ""

    if state.get("is_reroll", False):
        print("---REROLL MODE: Requesting different enhancement---")
        enhanced = llm_service.get_enhanced_prompt(
            state["original_prompt"],
            is_reroll=True,
            previous_enhancement=state.get("previous_enhancement"),
            recent_prompts=recent if recent else None,
            project_context=project_ctx if project_ctx else None,
        )
    else:
        enhanced = llm_service.get_enhanced_prompt(
            state["original_prompt"],
            recent_prompts=recent if recent else None,
            project_context=project_ctx if project_ctx else None,
        )
    return {"enhanced_prompt": enhanced, "retry_count": retry_count}

def save_results(state: GraphState):
    print("---NODE: SAVE RESULTS---")
    db = state["db"]
    enhanced_prompt = state["enhanced_prompt"]

    if llm_service.is_code(state["original_prompt"]):
        print("Skipping DB save for raw code.")
        return {}

    if enhanced_prompt is None:
        print("---WARNING: Enhancement failed. Skipping DB save.---")
        return {}

    project_id = state.get("project_id")
    existing_prompt = crud.get_prompt_by_original_text(db, state["original_prompt"], project_id=project_id)

    if existing_prompt:
        print(f"---Prompt already in cache (ID: {existing_prompt.id}). Using existing cache entry.---")
        if existing_prompt.enhanced_prompt != enhanced_prompt:
            print(f"---Updating cache with new enhancement (reroll detected)---")
            existing_prompt.enhanced_prompt = enhanced_prompt
            db.commit()
            db.refresh(existing_prompt)
        prompt_id = existing_prompt.id
    else:
        print(f"---Creating new cache entry---")
        prompt_to_cache = schemas.PromptCacheCreate(
            original_prompt=state["original_prompt"],
            enhanced_prompt=enhanced_prompt,
            project_id=project_id,
        )
        try:
            created_prompt_obj = crud.create_cached_prompt(db, prompt=prompt_to_cache)
            prompt_id = created_prompt_obj.id
        except Exception as e:
            if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
                print(f"---Cache entry already exists (race condition). Retrieving existing entry.---")
                existing_prompt = crud.get_prompt_by_original_text(db, state["original_prompt"], project_id=project_id)
                if existing_prompt:
                    prompt_id = existing_prompt.id
                else:
                    print(f"---ERROR: Could not find or create cache entry.---")
                    return {}
            else:
                raise

    if project_id:
        crud.create_prompt_history_entry(
            db,
            schemas.PromptHistoryCreate(
                project_id=project_id,
                user_id=state["user_id"],
                session_id=state["session_id"],
                original_prompt=state["original_prompt"],
                enhanced_prompt=enhanced_prompt,
            ),
        )

    if prompt_id:
        analytics_to_save = schemas.UsageAnalyticsCreate(
            prompt_id=prompt_id,
            user_id=state["user_id"],
            session_id=state["session_id"],
            enhancement_strategy="engineer_v3_groq_primary",
            user_action="accepted"
        )
        crud.create_usage_analytics_entry(db, analytics_data=analytics_to_save)
    return {"prompt_id": prompt_id}

def quality_filter(state: GraphState):
    """Use ML model to predict if enhancement will be accepted. Loop back if quality is low."""
    print("---NODE: QUALITY FILTER---")
    enhanced = state.get("enhanced_prompt")
    original = state.get("original_prompt")
    
    if not enhanced or not original:
        print("---WARNING: Missing prompts for quality check. Proceeding anyway.---")
        return {"quality_score": 1.0, "retry_count": state.get("retry_count", 0)}
    
    # Predict acceptance probability
    probability = ml_inference_service.predict_acceptance_probability(original, enhanced)
    
    print(f"---Quality Score: {probability:.4f} (threshold: 0.40)---")
    
    return {"quality_score": probability, "retry_count": state.get("retry_count", 0)}

workflow = StateGraph(GraphState)

workflow.add_node("check_cache", check_cache)
workflow.add_node("enhance_prompt", enhance_prompt)
workflow.add_node("quality_filter", quality_filter)
workflow.add_node("save_results", save_results)

def decide_next_step(state: GraphState):
    if state.get("enhanced_prompt") == state.get("original_prompt"): # is_code check returned original
        return END
    if state.get("from_cache"):
        return END
    return "enhance_prompt"

def after_quality_check(state: GraphState):
    """After quality check, either save (if good) or retry (if bad)."""
    quality = state.get("quality_score", 1.0)
    # Limit retries to prevent infinite loops (max 3 attempts)
    retry_count = state.get("retry_count", 0) or 0
    
    if quality < 0.40 and retry_count < 1:
        print(f"---RETRY #{retry_count + 1}: Quality too low, trying again---")
        return "enhance_prompt"  # Loop back to enhance (will increment retry_count)
    else:
        if retry_count >= 1:
            print("---MAX RETRIES REACHED: Saving anyway---")
        return "save_results"  # Proceed to save

workflow.set_entry_point("check_cache")
workflow.add_conditional_edges("check_cache", decide_next_step)
workflow.add_edge("enhance_prompt", "quality_filter")
workflow.add_conditional_edges("quality_filter", after_quality_check)
workflow.add_edge("save_results", END)

enhancement_graph = workflow.compile()