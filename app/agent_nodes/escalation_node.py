"""
Escalation node for handling requests that need human support.

This node is triggered when the system determines it cannot adequately
handle a user's request and needs to escalate to human support.
"""
from app.state.graph_states import GraphState
from app.data_models.escalation_models import (
    EscalationReason,
    EscalationContext,
    EscalationOutput
)
from app.types import EscalationReasonType, SeverityType
from typing import Dict
import uuid


def generate_ticket_id() -> str:
    """Generate a unique support ticket ID."""
    return f"TICKET-{uuid.uuid4().hex[:8].upper()}"


def escalation_node(state: GraphState) -> Dict:
    """
    Escalation node that handles requests needing human support.

    This node:
    1. Collects all context about the failed request
    2. Generates a support ticket
    3. Provides a user-friendly message
    4. Prepares context for the support team

    Args:
        state (GraphState): Current graph state

    Returns:
        dict: Updated state with escalation information
    """

    # Build escalation reasons list
    reasons = []
    for reason_text in state.escalation_reasons:
        # Parse reason type from text
        reason_type: EscalationReasonType = "system_error"  # default
        severity: SeverityType = "medium"

        if "clarification" in reason_text.lower():
            reason_type = "max_clarification_rounds"
            severity = "high"
        elif "confidence" in reason_text.lower():
            reason_type = "low_confidence"
            severity = "medium"
        elif "unsupported" in reason_text.lower() or "not supported" in reason_text.lower():
            reason_type = "unsupported_action"
            severity = "medium"
        elif "validation" in reason_text.lower() or "error" in reason_text.lower():
            reason_type = "validation_errors"
            severity = "low"
        elif "user" in reason_text.lower() or "request" in reason_text.lower():
            reason_type = "user_request"
            severity = "low"
        elif "ambig" in reason_text.lower():
            reason_type = "ambiguity_unresolved"
            severity = "high"

        reasons.append(
            EscalationReason(
                reason_type=reason_type,
                description=reason_text,
                severity=severity
            )
        )

    # Build escalation context
    context = EscalationContext(
        original_query=state.query or "No query provided",
        mode=state.mode,
        action_type=state.action_type,
        escalation_reasons=reasons,
        attempted_clarifications=state.clarify_round,
        clarification_history=state.clarification_history,
        collected_fields=state.collected_fields,
        missing_fields=state.missing_fields,
        confidence_score=None,  # Could be extracted from clarify node result
        error_messages=[state.error] if state.error else []
    )

    # Generate ticket
    ticket_id = generate_ticket_id()

    # Create user-friendly message
    primary_reason = reasons[0] if reasons else None

    if primary_reason:
        if primary_reason.reason_type == "max_clarification_rounds":
            user_message = (
                "I apologize, but I'm having difficulty gathering all the necessary information "
                "to complete your request. I've escalated this to our support team who will "
                "assist you directly."
            )
        elif primary_reason.reason_type == "low_confidence":
            user_message = (
                "I'm not confident I fully understand your request. To ensure we handle this "
                "correctly, I've connected you with our support team."
            )
        elif primary_reason.reason_type == "unsupported_action":
            user_message = (
                "This type of request requires specialized handling. I've escalated this to "
                "our support team who have the necessary tools to assist you."
            )
        elif primary_reason.reason_type == "ambiguity_unresolved":
            user_message = (
                "Your request has some ambiguities I cannot resolve automatically. "
                "Our support team will help clarify and process your request."
            )
        else:
            user_message = (
                "I've encountered an issue processing your request. Our support team "
                "has been notified and will assist you shortly."
            )
    else:
        user_message = (
            "I'm unable to complete this request automatically. "
            "Our support team will take over from here."
        )

    # Add ticket information
    user_message += f"\n\n📋 Support Ticket: {ticket_id}"
    user_message += "\n\nOur team will review your request and get back to you soon."

    # Build output
    escalation_output = EscalationOutput(
        escalated=True,
        escalation_message=user_message,
        support_ticket_id=ticket_id,
        context=context
    )

    # Log escalation (in production, would send to support system)
    print(f"\n🚨 ESCALATION: {ticket_id}")
    print(f"   Reason: {primary_reason.description if primary_reason else 'Unknown'}")
    print(f"   Query: {state.query}")
    print(f"   Clarification rounds: {state.clarify_round}/{state.max_clarify_rounds}")

    # Return state updates
    return {
        "escalated": True,
        "final_answer": user_message,
        "error": None  # Clear error since it's being handled by escalation
    }

