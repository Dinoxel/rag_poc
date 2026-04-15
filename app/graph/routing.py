'''
Routing logic for different user modes
includes:
- route_by_mode: routes to appropriate graph based on mode (q&a or task_execution)
- route_after_clarify: routes after clarification node based on missing fields
- route_after_confirmation: routes after scheduler confirmation based on confirmation status
'''

from app.state.graph_states import GraphState
from app.types.types import StateModeType


def route_by_mode(state: GraphState) -> StateModeType:
    """
    Receives the current GraphState:mode and routes to the appropriate graph based on mode
    Args:
        state: Current graph state with mode information
    Returns:
        str: Name of the graph to route to
    """
    if state.mode is not None:
        return state.mode

    return state.DEFAULT_STATE_MODE


from app.state.graph_states import GraphState


def route_after_clarify(state: GraphState):
    """
    Decide next step after clarification node.
    """
    if state.missing_fields:
        return "clarify_interrupt"
    return "task_execution_graph"


def route_after_confirmation(state: GraphState) -> str:
    """
    Decide next step after scheduler confirmation.
    """
    if state.scheduler_confirmed:
        return "answer"

    # If not confirmed, re-run scheduler
    return "scheduler"
