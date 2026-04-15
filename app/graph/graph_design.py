"""
Agentic System Graph Design

This module defines the complete LangGraph workflow for the agentic system.
The graph includes two main paths:
1. Q&A Path: RAG-based question answering
2. Task Execution Path: Clarification → Scheduler → Confirmation → Execution

Updated: 2026-04-15
Features:
- Advanced clarification agent with action type detection
- Field validation and normalization
- Human-in-the-loop for clarification and confirmation
- Max 3 clarification rounds to prevent infinite loops
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# State
from app.state.graph_states import GraphState

# Agent Nodes
from app.agent_nodes.planner_node import planner_node
from app.agent_nodes.retrieval_node import retrieval_node
from app.agent_nodes.query_clarify_node import clarify_node
from app.agent_nodes.scheduler_node import scheduler_node
from app.agent_nodes.confirm_scheduler_node import confirm_plan_node
from app.agent_nodes.answer_node import answer_node
from app.agent_nodes.escalation_node import escalation_node  # NEW: Escalation support

# Routing Functions
from app.graph.routing import (
    route_by_mode,
    route_after_clarify,
    route_after_confirmation
)


# ============================================================================
# GRAPH CONSTRUCTION
# ============================================================================

# Initialize StateGraph with GraphState
main_graph = StateGraph(GraphState)


# ----------------------------------------------------------------------------
# Add Nodes
# ----------------------------------------------------------------------------

# 1. Planner: Determines if request is Q&A or Task Execution
main_graph.add_node("planner", planner_node)

# 2. Q&A Graph: Retrieval-based question answering
main_graph.add_node("q&a_graph", retrieval_node)

# 3. Clarify Node: Advanced clarification agent
#    - Detects action type (create_invoice, send_quote, check_payment_status)
#    - Extracts provided fields
#    - Identifies missing required fields
#    - Interrupts for user input if needed
#    - Validates and normalizes collected data
main_graph.add_node("clarify_node", clarify_node)

# 4. Task Execution Graph: Scheduler/Planner for task execution
#    - Validates collected fields
#    - Generates action steps
main_graph.add_node("task_execution_graph", scheduler_node)

# 5. Confirm Plan Node: Human-in-the-loop confirmation
#    - Presents plan to user for approval
#    - Allows modifications
main_graph.add_node("confirm_plan_node", confirm_plan_node)

# 6. Answer Node: Final response generation
#    - Produces natural language response
#    - Handles both Q&A and Task Execution results
main_graph.add_node("answer_node", answer_node)

# 7. Escalation Node: Human support escalation (NEW - Tâche 2)
#    - Handles requests that cannot be processed automatically
#    - Generates support tickets
#    - Provides context to support team
main_graph.add_node("escalation_node", escalation_node)


# ----------------------------------------------------------------------------
# Add Edges
# ----------------------------------------------------------------------------

# Start: Always begin with planner
main_graph.add_edge(START, "planner")

# Planner Routing: Q&A, Task Execution, or Direct Escalation
main_graph.add_conditional_edges(
    "planner",
    route_by_mode,
    {
        "q&a": "q&a_graph",              # Q&A path
        "task_execution": "clarify_node",  # Task Execution path
        "escalate": "escalation_node"      # Direct escalation (NEW)
    }
)

# Q&A Path: Retrieval → Answer → End
main_graph.add_edge("q&a_graph", "answer_node")

# Clarification Routing: Loop if missing fields, continue if complete, escalate if needed
main_graph.add_conditional_edges(
    "clarify_node",
    route_after_clarify,
    {
        "clarify_interrupt": "clarify_node",                # Loop back if missing fields
        "escalate": "escalation_node",                      # NEW: Escalate if needed
        "task_execution_graph": "task_execution_graph"      # Continue if complete
    }
)

# Task Execution: Scheduler → Confirmation
main_graph.add_edge("task_execution_graph", "confirm_plan_node")

# Confirmation Routing: Answer if confirmed, re-schedule if rejected
main_graph.add_conditional_edges(
    "confirm_plan_node",
    route_after_confirmation,
    {
        "answer": "answer_node",              # Confirmed → Answer
        "scheduler": "task_execution_graph"   # Rejected → Re-schedule
    }
)

# Answer: Always end after answer
main_graph.add_edge("answer_node", END)

# Escalation: End after escalation (support takes over)
main_graph.add_edge("escalation_node", END)


# ----------------------------------------------------------------------------
# Compile Graph with Checkpointer
# ----------------------------------------------------------------------------

# MemorySaver enables:
# - State persistence across interrupts
# - Human-in-the-loop capabilities
# - Resumable workflows
checkpointer = MemorySaver()
poc_graph = main_graph.compile(checkpointer=checkpointer)


# ----------------------------------------------------------------------------
# Generate Visualization
# ----------------------------------------------------------------------------

# Generate PNG diagram of the graph
graph_pic = poc_graph.get_graph().draw_mermaid_png()
with open("./graph_diagram.png", "wb") as f:
    f.write(graph_pic)

print("✅ Graph compiled successfully!")
print("📊 Graph diagram saved as: graph_diagram.png")
print("\nGraph Structure:")
print("  START → planner")
print("    ├─→ Q&A: retrieval → answer → END")
print("    ├─→ Task: clarify (loop/escalate) → scheduler → confirm (loop) → answer → END")
print("    │         └─→ escalation → END (from clarify)")
print("    └─→ Escalate: escalation → END (direct from planner) ⭐ NEW")
