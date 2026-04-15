# app/agents/nodes/retrieval_node.py
"""
retrieval node for retrieving relevant documents based on query
"""

from app.tools.agent_tools import similarity_search_with_score_tool
from app.state.graph_states import GraphState


def retrieval_node(state: GraphState) -> dict:
    """
    Graph node responsible ONLY for retrieval.
    """

    print("\n[RETRIEVAL NODE] Starting...")
    print(f"  - Query: {state.query}")

    if not state.query:
        error_msg = "Missing query for retrieval"
        print(f"  Error: {error_msg}\n")
        return {"error": error_msg}

    try:
        retrieved_context = similarity_search_with_score_tool.invoke(
            {"query": state.query, "k": 3}
        )


    except Exception as e:
        error_msg = f"Retrieval failed: {e}"
        print(f"  Error: {error_msg}\n")
        import traceback
        traceback.print_exc()
        return {"error": error_msg}

    return {
        "retrieved_context": retrieved_context

    }
