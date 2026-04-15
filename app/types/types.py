from typing import Literal

StateModeType = Literal["q&a", "task_execution", "escalate"]

EscalationReasonType = Literal[
    "max_clarification_rounds",
    "low_confidence",
    "unsupported_action",
    "validation_errors",
    "user_request",
    "ambiguity_unresolved",
    "system_error"
]

SeverityType = Literal["low", "medium", "high"]