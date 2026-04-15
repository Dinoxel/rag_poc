"""
this file contains a confirmation node that asks the user to confirm the generated action steps from the scheduler.
"""
from langgraph.types import interrupt
from app.state.graph_states import GraphState


def confirm_plan_node(state: GraphState):
    """
    Ask the user to confirm the generated action plan.
    Args:
        state: Current graph state with proposed action steps
    Returns:
        dict with scheduler_confirmed (bool) -- yes / no
    """

    decision = interrupt({
        "kind": "confirm",
        "action_steps": state.action_steps
    })

    # decision from user 
    decision_normalized = str(decision).strip().lower()

    if decision_normalized in ["yes", "y", "confirm", "approved"]:
        return {"scheduler_confirmed": True}

    return {"scheduler_confirmed": False}
