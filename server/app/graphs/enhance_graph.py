from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from app.crud import prompt_cache as crud
from sqlalchemy.orm import Session

# --- 1. Define the State ---
# This dictionary represents the data that flows through our graph.
class GraphState(TypedDict):
    original_prompt: str
    enhanced_prompt: str | None
    from_cache: bool
    db: Session

# --- 2. Define the Nodes ---
# Each node is a function that performs an action and modifies the state.

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

def enhance_with_llm(state: GraphState):
    """
    Placeholder for the actual LLM call.
    In the future, this will call Groq/Gemini.
    """
    print("---NODE: ENHANCE WITH LLM (PLACEHOLDER)---")
    original_prompt = state["original_prompt"]
    
    # This is a dummy enhancement logic for now
    enhanced_version = f"**Enhanced by LLM:** {original_prompt.title()} using a sophisticated Python design pattern."
    
    return {"enhanced_prompt": enhanced_version}

def save_to_cache(state: GraphState):
    """Saves the newly enhanced prompt to the cache."""
    print("---NODE: SAVE TO CACHE---")
    db = state["db"]
    original_prompt = state["original_prompt"]
    enhanced_prompt = state["enhanced_prompt"]

    if original_prompt and enhanced_prompt:
        crud.create_cached_prompt(
            db,
            prompt={"original_prompt": original_prompt, "enhanced_prompt": enhanced_prompt}
        )
    return {}


# --- 3. Define the Edges ---
# This function determines which node to go to next.
def decide_to_enhance(state: GraphState) -> Literal["enhance_with_llm", "__end__"]:
    """
    Conditional edge. If the prompt was found in the cache, we finish.
    Otherwise, we call the LLM to enhance it.
    """
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

    # Add the nodes
    workflow.add_node("check_cache", check_cache)
    workflow.add_node("enhance_with_llm", enhance_with_llm)
    workflow.add_node("save_to_cache", save_to_cache)
    
    # Set the entry point
    workflow.set_entry_point("check_cache")
    
    # Add the edges
    workflow.add_edge("enhance_with_llm", "save_to_cache")
    workflow.add_edge("save_to_cache", END)
    
    # Add the conditional edge
    workflow.add_conditional_edges(
        "check_cache",
        decide_to_enhance
    )
    
    # Compile the graph into a runnable app
    return workflow.compile()

enhancement_graph = create_enhancement_graph()