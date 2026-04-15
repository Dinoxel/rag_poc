'''
the scheduler_node generates an execution plan (action steps) for a clarified task. 

'''
from app.state.graph_states import GraphState
from app.prompts.agent_prompts import SCHEDULER_PROMPT
from app.data_models.models import SchedulerOutput
from app.core.config import llm_generation

# Create scheduler chain
scheduler_chain = (
        SCHEDULER_PROMPT
        | llm_generation.with_structured_output(SchedulerOutput)
)


def scheduler_node(state: GraphState) -> dict:
    """
    Generate an execution plan (action steps) for the clarified task.
    This node does NOT execute the task.
    """

    # Construct input for the scheduler
    input_text = (
        f"Original query: {state.query}\n"
        f"Required fields:\n"
    )

    for key, value in state.collected_fields.items():
        input_text += f"- {key}: {value}\n"

    # Invoke scheduler LLM
    result = scheduler_chain.invoke({
        "input": input_text
    })

    return {
        "action_steps": result.action_steps
    }
