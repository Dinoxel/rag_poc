"""
Data models for structured outputs from agents.
"""
from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class PlannerOutput(BaseModel):
    """Output model for planner agent."""
    mode: str = Field(description="Either 'q&a' or 'task_execution'")


class ClarifyOutput(BaseModel):
    """Output model for clarify agent."""
    collected_fields: Optional[Dict[str, str]] = Field(default=None, description="Fields that were provided")
    missing_fields: Optional[List[str]] = Field(default=None, description="Required fields that are missing")


class SchedulerOutput(BaseModel):
    """
    Output of the scheduler/planning step.
    """
    action_steps: List[str] = Field(description="List of action steps to be taken")
