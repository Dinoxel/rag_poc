"""
this file contains the answer node for both Q&A and task execution flows.
"""

from app.prompts.agent_prompts import ANSWER_PROMPT
from app.core.config import llm_generation
from app.state.graph_states import GraphState

answer_chain = ANSWER_PROMPT | llm_generation


def answer_node(state: GraphState) -> dict:
    """
    Unified answer node for both Q&A and task execution flows.
    Args:
        state: Current graph state with necessary information
    Returns:
        dict with final_answer (str) -- the final response to the user
    """

    if state.mode == "q&a":
        input_text = f"""
                        User question:
                        {state.query}

                        Retrieved context:
                        {state.retrieved_context}
                    """

    elif state.mode == "task_execution":
        if state.scheduler_confirmed:
            steps_text = "\n".join(
                f"{idx + 1}. {step}" for idx, step in enumerate(state.action_steps)
            )

        input_text = f"""
                        User request:
                        {state.query}

                        Confirmed action plan:
                        {steps_text}
                    """

    else:
        return {
            "final_answer": "I'm not sure how to handle this request."
        }

    final_answer = answer_chain.invoke({
        "input": input_text
    })

    return {
        "final_answer": final_answer
    }
