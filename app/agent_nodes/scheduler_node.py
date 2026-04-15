'''
the scheduler_node generates an execution plan (action steps) for a clarified task. 

'''
from app.state.graph_states import GraphState
from app.prompts.agent_prompts import SCHEDULER_PROMPT
from app.data_models.models import SchedulerOutput
from app.core.config import llm_generation
from app.tools.field_validators import validate_collected_fields

# Create scheduler chain
scheduler_chain = (
        SCHEDULER_PROMPT
        | llm_generation.with_structured_output(SchedulerOutput)
)


def scheduler_node(state: GraphState) -> dict:
    """
    Generate an execution plan (action steps) for the clarified task.
    This node does NOT execute the task.

    Process:
    1. Validate collected fields based on action type
    2. Build context for scheduler with action type and validated fields
    3. Generate ordered action steps
    4. Return action plan
    """

    # 1. Validate collected fields if action_type is known
    validated_fields = state.collected_fields
    validation_errors = []

    if state.action_type:
        validated_fields, validation_errors = validate_collected_fields(
            state.collected_fields,
            state.action_type
        )

        if validation_errors:
            # Return error state if validation fails
            return {
                "error": "Field validation errors: " + "; ".join(validation_errors)
            }

    # 2. Construct input for the scheduler
    input_text = f"Action Type: {state.action_type or 'Generic Task'}\n\n"
    input_text += f"Original query: {state.query}\n\n"
    input_text += "Collected and validated fields:\n"

    for key, value in validated_fields.items():
        input_text += f"- {key}: {value}\n"

    # 3. Invoke scheduler LLM
    result = scheduler_chain.invoke({
        "input": input_text
    })

    # 4. Return action plan
    return {
        "action_steps": result.action_steps,
        "collected_fields": validated_fields  # Update with validated values
    }
