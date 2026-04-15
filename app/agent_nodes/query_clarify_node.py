"""
This file contains the clarify agent chain and clarify node
"""
from app.prompts.agent_prompts import CLARIFY_PROMPT
from app.data_models.models import ClarifyOutput
from app.core.config import llm_generation
from app.state.graph_states import GraphState
from langgraph.types import interrupt
from typing import Dict, Any


# Create clarify chain
clarify_chain = (
        CLARIFY_PROMPT | llm_generation.with_structured_output(ClarifyOutput)
)


def format_missing_fields_for_user(missing_fields) -> Dict[str, Any]:
    """
    Format missing fields into a user-friendly structure for interruption.
    Groups fields by required/optional and includes suggestions.
    """
    required_fields = []
    optional_fields = []

    for field in missing_fields:
        field_info = {
            "field_name": field.field_name,
            "question": field.question,
            "type": field.field_type,
        }

        # Add suggestions for choice fields
        if field.suggested_values:
            field_info["options"] = field.suggested_values

        # Add validation hints
        if field.validation_hint:
            field_info["format"] = field.validation_hint

        if field.is_required:
            required_fields.append(field_info)
        else:
            optional_fields.append(field_info)

    return {
        "required": required_fields,
        "optional": optional_fields,
    }


def clarify_node(state: GraphState) -> dict:
    """
    Advanced clarify node to identify missing information in the user's query.

    Capabilities:
    - Detects action type (create_invoice, send_quote, check_payment_status)
    - Extracts explicitly provided fields
    - Identifies missing required and optional fields
    - Provides structured questions with type information and suggestions
    - Validates confidence and detects ambiguity
    - Interrupts graph when clarification is needed

    Args:
        state (GraphState): Current state of the graph containing the user query and clarification history.

    Returns:
        dict: Updated state with action type, missing fields, collected fields, and metadata.

    Process:
    1. Check if max clarification rounds reached
    2. Build input from original query and clarification history
    3. Invoke LLM to analyze and extract information
    4. If missing required fields found, interrupt for user input
    5. Update state with extracted information and metadata
    """

    # 1. Check clarification round limit
    if state.clarify_round >= state.max_clarify_rounds:
        # Escalate: max rounds reached
        return {
            "missing_fields": [],
            "should_escalate": True,
            "escalation_reasons": [
                f"Maximum clarification rounds ({state.max_clarify_rounds}) reached. "
                f"Unable to collect all required information."
            ],
            "error": None  # Clear error since we're escalating
        }

    # 2. Build input context
    input_text = f"Original query: {state.query}\n"
    if state.clarification_history:
        input_text += "\nClarifications provided by user:\n"
        for idx, clarification in enumerate(state.clarification_history, 1):
            input_text += f"{idx}. {clarification}\n"

    # 3. Invoke LLM for analysis
    result: ClarifyOutput = clarify_chain.invoke({
        "input": input_text
    })

    # Extract results
    action_type = result.action_type
    new_collected_fields = result.collected_fields or {}
    new_missing_fields = result.missing_fields or []
    confidence = result.confidence_score
    is_ambiguous = result.is_ambiguous

    # Log ambiguity warning
    if is_ambiguous and result.ambiguity_reason:
        print(f"⚠️  Ambiguity detected: {result.ambiguity_reason}")

    # Check for escalation conditions
    should_escalate = False
    escalation_reasons = []

    # Escalation condition 1: Very low confidence
    if confidence < 0.3:
        should_escalate = True
        escalation_reasons.append(
            f"Very low confidence score ({confidence:.2f}). Unable to reliably understand the request."
        )

    # Escalation condition 2: Unsupported action type
    if action_type and action_type not in ["create_invoice", "send_quote", "check_payment_status"]:
        should_escalate = True
        escalation_reasons.append(
            f"Unsupported action type detected: '{action_type}'. This request requires specialized handling."
        )

    # Escalation condition 3: Persistent ambiguity after multiple rounds
    if is_ambiguous and state.clarify_round >= 2:
        should_escalate = True
        escalation_reasons.append(
            f"Persistent ambiguity after {state.clarify_round} clarification rounds. {result.ambiguity_reason}"
        )

    # If should escalate, return immediately
    if should_escalate:
        return {
            "action_type": action_type,
            "collected_fields": {
                **state.collected_fields,
                **new_collected_fields,
            },
            "missing_fields": [],
            "should_escalate": True,
            "escalation_reasons": escalation_reasons
        }

    # Filter to only required missing fields for interruption
    # (we prioritize required fields in early rounds)
    required_missing = [f for f in new_missing_fields if f.is_required]

    # If we still have rounds left and there are optional fields,
    # we can ask for them too, but prioritize required
    fields_to_ask = required_missing if required_missing else new_missing_fields[:5]

    # 4. If missing → interrupt with structured format
    if fields_to_ask:
        formatted_fields = format_missing_fields_for_user(fields_to_ask)

        user_input = interrupt({
            "kind": "clarify",
            "action_type": action_type,
            "missing_fields": formatted_fields,
            "confidence": confidence,
            "is_ambiguous": is_ambiguous,
            "ambiguity_reason": result.ambiguity_reason,
        })

        # Convert missing fields to simple list for state storage
        missing_field_names = [f.field_name for f in fields_to_ask]

        return {
            "action_type": action_type,
            "clarification_history": state.clarification_history + [user_input],
            "missing_fields": missing_field_names,
            "collected_fields": {
                **state.collected_fields,
                **new_collected_fields,
            },
            "clarify_round": state.clarify_round + 1,
        }

    # 5. No missing required fields → update state and continue
    return {
        "action_type": action_type,
        "missing_fields": [],
        "collected_fields": {
            **state.collected_fields,
            **new_collected_fields,
        }
    }
