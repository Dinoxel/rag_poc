# graph.py
from langgraph.graph import StateGraph, START, END
from app.state.graph_states import GraphState
from app.agent_nodes.planner_node import planner_node
from app.graph.routing import route_by_mode, route_after_confirmation, route_after_clarify
from app.agent_nodes.retrieval_node import retrieval_node
from app.agent_nodes.query_clarify_node import clarify_node
from app.agent_nodes.scheduler_node import scheduler_node
from app.agent_nodes.confirm_scheduler_node import confirm_plan_node
from app.agent_nodes.answer_node import answer_node
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles
from langgraph.checkpoint.memory import MemorySaver

main_graph = StateGraph(GraphState)

main_graph.add_node("planner", planner_node)
main_graph.add_node("q&a_graph", retrieval_node)
main_graph.add_node("clarify_node", clarify_node)
main_graph.add_node("task_execution_graph", scheduler_node)
main_graph.add_node("confirm_plan_node", confirm_plan_node)
main_graph.add_node("answer_node", answer_node)

main_graph.add_edge(START, "planner")

main_graph.add_conditional_edges(
    "planner",
    route_by_mode,
    {
        "q&a": "q&a_graph",
        "task_execution": "clarify_node"
    }
)

main_graph.add_edge("q&a_graph", "answer_node")
main_graph.add_conditional_edges(
    "clarify_node",
    route_after_clarify,
    {
        "clarify_interrupt": "clarify_node",  # 注意：loop
        "task_execution_graph": "task_execution_graph"
    }
)

main_graph.add_edge("task_execution_graph", "confirm_plan_node")
main_graph.add_conditional_edges(
    "confirm_plan_node",
    route_after_confirmation,
    {
        "answer": "answer_node",
        "scheduler": "task_execution_graph"
    }
)
main_graph.add_edge("answer_node", END)

checkpointer = MemorySaver()
poc_graph = main_graph.compile(checkpointer=checkpointer)

# visualize
graph_pic = poc_graph.get_graph().draw_mermaid_png()
with open("./graph_diagram.png", "wb") as f:
    f.write(graph_pic)
print("Graph diagram saved as graph_diagram.png")
