'''
this file contains the planner agent chain and planner node
'''
from app.prompts.agent_prompts import PLANNER_PROMPT
from app.data_models.models import PlannerOutput
from app.core.config import llm_generation
from app.state.graph_states import GraphState

# ---------------- Planner Agent Chain----------------
planner_agent = (
        PLANNER_PROMPT | llm_generation.with_structured_output(PlannerOutput)
)


def planner_node(state: GraphState) -> dict:
    """
    Planner node that detects user intent and system mode.
    
    Args:
        state: Current graph state with messages
        
    Returns:
        dict with mode
    """
    user_message = state.messages[-1]

    result = planner_agent.invoke(
        {"input": user_message.content}
    )

    return {
        "mode": result.mode
    }
