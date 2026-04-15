'''
This file contains the clarify agent chain and clarify node
'''
from app.prompts.agent_prompts import CLARIFY_PROMPT
from app.data_models.models import ClarifyOutput
from app.core.config import llm_generation
from app.state.graph_states import GraphState
from langgraph.types import interrupt

# Create clarify chain
clarify_chain = (
        CLARIFY_PROMPT | llm_generation.with_structured_output(ClarifyOutput)
)


def clarify_node(state: GraphState) -> dict:
    '''
    Clarify node to identify missing information in the user's query.
    If missing information is found, interrupts the graph to request clarification from the user.
    Args:
        state (GraphState): Current state of the graph containing the user query and clarification history.
    Returns:
        dict: Updated state with missing fields and collected fields.
    1. Invoke LLM to identify missing fields based on the original query and clarification history
    2. If missing fields are found, interrupt the graph to request clarification from the user
    3. If no missing fields, update the state with collected fields and continue
    4. Limit the number of clarification rounds: 2
    '''

    if state.clarify_round >= state.max_clarify_rounds:
        return {
            "missing_fields": []
        }

    input_text = f"Original query: {state.query}\n"
    if state.clarification_history:
        input_text += "Clarifications provided:\n"
        for clarification in state.clarification_history:
            input_text += f"- {clarification}\n"

    # 1. Invoke LLM
    result = clarify_chain.invoke({
        "input": input_text
    })

    # 2️. USE result, not state
    new_missing_fields = result.missing_fields or []
    new_collected_fields = result.collected_fields or {}

    # 3. If missing → interrupt
    if new_missing_fields:
        user_input = interrupt({
            "kind": "clarify",
            "missing_fields": new_missing_fields,
        })

        return {
            "clarification_history": state.clarification_history + [user_input],
            "missing_fields": new_missing_fields,
            "collected_fields": {
                **state.collected_fields,
                **new_collected_fields,
            },
            "clarify_round": state.clarify_round + 1,
        }

    # 4.  No missing → update state and continue
    return {
        "missing_fields": [],
        "collected_fields": {
            **state.collected_fields,
            **new_collected_fields,
        }
    }
