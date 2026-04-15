from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from langchain_core.messages import AnyMessage
from app.types import StateModeType


class GraphState(BaseModel):
    DEFAULT_STATE_MODE: StateModeType = "q&a"

    # conversational context
    messages: List[AnyMessage] = Field(default_factory=list)

    query: Optional[str] = None

    # planner node (validated)
    mode: StateModeType = None           # "q&a" | "task_execution" | "escalate"

    # -------- q&a --------
    # retrieval
    retrieved_context: Optional[str] = None
    retrieval_artifacts: Optional[List[Dict]] = None


    # -------- task execution --------
    # action type detection
    action_type: Optional[str] = None  # "create_invoice", "send_quote", "check_payment_status"

    # extracted / clarified task info
    collected_fields: Dict[str, Optional[str]] = Field(default_factory=dict)

    # human-in-the-loop
    clarification_history: List[str] = Field(default_factory=list)
    missing_fields: List[str] = Field(default_factory=list)
    scheduler_confirmed: Optional[bool] = None
    clarify_round: int = 0
    max_clarify_rounds: int = 2

    # scheduler
    action_steps: List[str] = Field(default_factory=list)
    error: Optional[str] = None

    # escalation
    should_escalate: bool = False
    escalation_reasons: List[str] = Field(default_factory=list)
    escalated: bool = False

    # final answer / result
    final_answer: Optional[str] = None
