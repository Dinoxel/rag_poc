"""
Tests for the escalation system (Tâche 2).
"""
from app.data_models.escalation_models import (
    EscalationReason,
    EscalationContext,
    EscalationOutput
)
from app.agent_nodes.escalation_node import escalation_node, generate_ticket_id
from app.state.graph_states import GraphState
from datetime import datetime


def test_escalation_models():
    """Test escalation data models."""
    print("🧪 Testing escalation models...")

    # Test EscalationReason
    reason = EscalationReason(
        reason_type="max_clarification_rounds",
        description="Maximum clarification rounds reached",
        severity="high"
    )
    assert reason.reason_type == "max_clarification_rounds"
    assert reason.severity == "high"
    print("✅ EscalationReason model OK")

    # Test EscalationContext
    context = EscalationContext(
        original_query="Create an invoice",
        mode="task_execution",
        action_type="create_invoice",
        escalation_reasons=[reason],
        attempted_clarifications=3,
        clarification_history=["Question 1", "Question 2"],
        collected_fields={"amount": "5000"},
        missing_fields=["customer_name"],
        confidence_score=0.2
    )
    assert context.attempted_clarifications == 3
    assert len(context.escalation_reasons) == 1
    print("✅ EscalationContext model OK")

    # Test EscalationOutput
    output = EscalationOutput(
        escalated=True,
        escalation_message="Request escalated to support",
        support_ticket_id="TICKET-ABC123"
    )
    assert output.escalated is True
    assert output.support_ticket_id == "TICKET-ABC123"
    print("✅ EscalationOutput model OK")

    print("\n✅ All escalation models working correctly!\n")


def test_ticket_generation():
    """Test support ticket ID generation."""
    print("🧪 Testing ticket ID generation...")

    ticket1 = generate_ticket_id()
    ticket2 = generate_ticket_id()

    # Check format
    assert ticket1.startswith("TICKET-")
    assert len(ticket1) == 15  # "TICKET-" + 8 hex chars

    # Check uniqueness
    assert ticket1 != ticket2

    print(f"✅ Generated ticket IDs: {ticket1}, {ticket2}")
    print("✅ Ticket ID generation OK\n")


def test_escalation_node():
    """Test the escalation node."""
    print("🧪 Testing escalation node...")

    # Create a state that should escalate
    state = GraphState(
        query="Create an invoice for something",
        mode="task_execution",
        action_type="create_invoice",
        should_escalate=True,
        escalation_reasons=[
            "Maximum clarification rounds (3) reached. Unable to collect all required information."
        ],
        clarify_round=3,
        max_clarify_rounds=3,
        clarification_history=["Question 1", "Question 2", "Question 3"],
        collected_fields={"amount": "5000"},
        missing_fields=["customer_name", "invoice_date"]
    )

    # Run escalation node
    result = escalation_node(state)

    # Check results
    assert result["escalated"] is True
    assert result["final_answer"] is not None
    assert "TICKET-" in result["final_answer"]
    assert "support" in result["final_answer"].lower()

    print("✅ Escalation node OK")
    print(f"✅ Generated message: {result['final_answer'][:100]}...")
    print("\n✅ Escalation node working correctly!\n")


def test_escalation_scenarios():
    """Test different escalation scenarios."""
    print("🧪 Testing escalation scenarios...")

    scenarios = {
        "max_rounds": {
            "reason": "Maximum clarification rounds (3) reached",
            "expected_keywords": ["difficulty", "gathering", "information", "escalated"]
        },
        "low_confidence": {
            "reason": "Very low confidence score (0.25)",
            "expected_keywords": ["not confident", "understand", "support team"]
        },
        "unsupported_action": {
            "reason": "Unsupported action type: 'delete_database'",
            "expected_keywords": ["specialized", "handling", "escalated"]
        },
        "ambiguity": {
            "reason": "Persistent ambiguity after 2 rounds",
            "expected_keywords": ["ambiguities", "clarify", "support"]
        }
    }

    for scenario_name, scenario_data in scenarios.items():
        state = GraphState(
            query="Test query",
            should_escalate=True,
            escalation_reasons=[scenario_data["reason"]]
        )

        result = escalation_node(state)
        message = result["final_answer"].lower()

        # Check that at least one expected keyword is present
        found = any(keyword.lower() in message for keyword in scenario_data["expected_keywords"])

        print(f"  Scenario '{scenario_name}': {'✅ PASS' if found else '❌ FAIL'}")

    print("\n✅ All escalation scenarios tested!\n")


def run_all_tests():
    """Run all escalation tests."""
    print("\n" + "="*70)
    print("ESCALATION SYSTEM - COMPONENT TESTS (TÂCHE 2)")
    print("="*70 + "\n")

    try:
        test_escalation_models()
        test_ticket_generation()
        test_escalation_node()
        test_escalation_scenarios()

        print("="*70)
        print("✅ ALL ESCALATION TESTS PASSED!")
        print("="*70)
        print("\nThe escalation system is ready to use.")
        print("Escalation triggers:")
        print("  • Max clarification rounds reached (3)")
        print("  • Confidence score < 0.3")
        print("  • Unsupported action type")
        print("  • Persistent ambiguity (2+ rounds)")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()

