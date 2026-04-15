"""
Escalation data models.

Defines the structure and reasons for escalating requests to human support.
"""
from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from app.types import EscalationReasonType, SeverityType


class EscalationReason(BaseModel):
    """Represents a specific reason for escalation."""

    reason_type: EscalationReasonType = Field(description="Type of escalation reason")

    description: str = Field(description="Human-readable description of the issue")

    severity: SeverityType = Field(
        default="medium",
        description="Severity level of the escalation"
    )

    details: Optional[dict] = Field(
        default=None,
        description="Additional context about the escalation"
    )


class EscalationContext(BaseModel):
    """Complete context for an escalated request."""

    original_query: str = Field(description="User's original query")

    mode: Optional[str] = Field(
        default=None,
        description="Detected mode (q&a or task_execution)"
    )

    action_type: Optional[str] = Field(
        default=None,
        description="Detected action type if task execution"
    )

    escalation_reasons: List[EscalationReason] = Field(
        description="List of reasons for escalation"
    )

    attempted_clarifications: int = Field(
        default=0,
        description="Number of clarification rounds attempted"
    )

    clarification_history: List[str] = Field(
        default_factory=list,
        description="History of clarification exchanges"
    )

    collected_fields: dict = Field(
        default_factory=dict,
        description="Fields collected so far"
    )

    missing_fields: List[str] = Field(
        default_factory=list,
        description="Fields still missing"
    )

    confidence_score: Optional[float] = Field(
        default=None,
        description="Confidence score if available"
    )

    error_messages: List[str] = Field(
        default_factory=list,
        description="Any error messages encountered"
    )

    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the escalation occurred"
    )


class EscalationOutput(BaseModel):
    """Output of the escalation node."""

    escalated: bool = Field(description="Whether the request was escalated")

    escalation_message: str = Field(
        description="Message to display to the user about escalation"
    )

    support_ticket_id: Optional[str] = Field(
        default=None,
        description="Generated support ticket ID"
    )

    context: Optional[EscalationContext] = Field(
        default=None,
        description="Full escalation context for support team"
    )

