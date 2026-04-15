"""
Data models for structured outputs from agents.
"""
from typing import Optional, Dict, List, get_args, Literal
from pydantic import BaseModel, Field
from app.types import StateModeType


class PlannerOutput(BaseModel):
    """Output model for planner agent."""
    mode: str = Field(description='Choices: "' + '", "'.join(get_args(StateModeType)) + '"')


class MissingField(BaseModel):
    """Represents a missing field that needs clarification."""
    field_name: str = Field(description="The name/identifier of the missing field")
    question: str = Field(description="The question to ask the user to get this information")
    field_type: Literal["text", "email", "amount", "date", "id", "choice"] = Field(
        description="Type of the field"
    )
    is_required: bool = Field(default=True, description="Whether this field is mandatory")
    suggested_values: Optional[List[str]] = Field(
        default=None,
        description="Suggested values for choice type fields"
    )
    validation_hint: Optional[str] = Field(
        default=None,
        description="Hint about expected format (e.g., 'YYYY-MM-DD', 'positive number')"
    )


class ClarifyOutput(BaseModel):
    """Output model for clarify agent."""
    action_type: Optional[str] = Field(
        default=None,
        description="The type of action detected (e.g., 'create_invoice', 'send_quote', 'check_payment_status')"
    )
    collected_fields: Optional[Dict[str, str]] = Field(
        default=None,
        description="Fields that were successfully extracted from the user's input"
    )
    missing_fields: Optional[List[MissingField]] = Field(
        default=None,
        description="Required or important fields that are missing and need clarification"
    )
    confidence_score: float = Field(
        default=1.0,
        ge=0,
        le=1,
        description="Confidence level in the extraction (0-1)"
    )
    is_ambiguous: bool = Field(
        default=False,
        description="Whether the user's request is ambiguous or unclear"
    )
    ambiguity_reason: Optional[str] = Field(
        default=None,
        description="Explanation of why the request is ambiguous, if applicable"
    )


class SchedulerOutput(BaseModel):
    """
    Output of the scheduler/planning step.
    """
    action_steps: List[str] = Field(description="List of action steps to be taken")
