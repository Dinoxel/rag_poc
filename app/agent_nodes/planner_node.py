"""
this file contains the planner agent chain and planner node
"""
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
    
    Modes:
    - "q&a": Information seeking, questions
    - "task_execution": Action requests (invoices, quotes, payments)
    - "escalate": Direct escalation to human support

    Args:
        state: Current graph state with messages
        
    Returns:
        dict with mode and optional escalation info
    """
    user_message = state.messages[-1]

    result = planner_agent.invoke(
        {"input": user_message.content}
    )

    # If escalate mode, prepare escalation info
    if result.mode == "escalate":
        return {
            "mode": result.mode,
            "should_escalate": True,
            "escalation_reasons": [
                "User request requires human support (detected by planner)"
            ]
        }

    return {
        "mode": result.mode
    }
