'''
this is a CLI application that interacts with an agentic system graph. It prompts the user for input, processes it through the graph,
and handles any interruptions that require human-in-the-loop clarifications or confirmations.
'''
from langgraph.types import Command
from langchain_core.messages import HumanMessage
from app.state.graph_states import GraphState
from app.graph.graph_design import poc_graph


def run_graph_cli():
    print("=== Agentic System CLI ===")
    print("Please enter your request:\n")

    # initial user query
    user_query = input("> ")
    while user_query.strip() == "":
        print("Input cannot be empty. Please enter your request:")
        user_query = input("> ")

    # initialize GraphState
    initial_state = GraphState(
        query=user_query,
        messages=[HumanMessage(content=user_query)]
    )

    # thread config
    config = {
        "configurable": {
            "thread_id": "main-graph-cli"
        }
    }

    # invoke graph
    print("Invoking graph...\n")
    result = poc_graph.invoke(initial_state, config=config)

    print(f"  - Mode: {result.get('mode')}")
    print(
        f"  - Retrieved Context: {result.get('retrieved_context')[:100] if result.get('retrieved_context') else None}...")
    print(f"  - Error: {result.get('error')}")
    print(f"  - Missing Fields: {result.get('missing_fields')}")
    print(f"  - Has Interrupt: {'__interrupt__' in result}\n")

    # handle interrupts (clarify / confirm)
    while "__interrupt__" in result:
        interrupt_obj = result["__interrupt__"][0]
        interrupt_info = interrupt_obj.value

        print("\n=== ACTION REQUIRED ===")

        if interrupt_info.get("kind") == "clarify":
            print("I need some additional information to continue.")
            print("Missing fields:")
            for field in interrupt_info.get("missing_fields", []):
                print(f"- {field}")
            print("\nPlease provide the missing information:")

        elif interrupt_info.get("kind") == "confirm":
            print("Please review the proposed plan:\n")
            for idx, step in enumerate(interrupt_info.get("action_steps", []), start=1):
                print(f"{idx}. {step}")
            print("\nDo you confirm this plan? (yes/no)")

        else:
            print("Input required:")
            print(interrupt_info)

        # user input
        user_response = input("> ")

        # resume graph
        result = poc_graph.invoke(
            Command(resume=user_response),
            config=config
        )

    print("\n=== FINAL ANSWER ===")
    print(
        result.get("final_answer").content
        if result.get("final_answer")
        else "No answer generated"
    )


if __name__ == "__main__":
    run_graph_cli()
