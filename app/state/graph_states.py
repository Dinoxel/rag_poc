from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from langchain_core.messages import AnyMessage
from app.types.types import StateModeType


class GraphState(BaseModel):
    DEFAULT_STATE_MODE: StateModeType = "q&a"

    # conversational context
    messages: List[AnyMessage] = Field(default_factory=list)

    query: Optional[str] = None

    # planner node (validated)
    mode: StateModeType = None           # "qa" | "task_execution"

    # -------- q&a --------
    # retrieval
    retrieved_context: Optional[str] = None
    retrieval_artifacts: Optional[List[Dict]] = None


    # -------- task execution --------
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

    # final answer / result
    final_answer: Optional[str] = None
