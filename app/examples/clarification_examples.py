"""
Example scenarios for testing the clarification agent.

This file contains example user queries and their expected clarification flow.
"""

EXAMPLE_SCENARIOS = {
    "complete_invoice": {
        "query": "Create an invoice for Acme Corp for €5000 dated 2024-03-15 for consulting services",
        "expected_action_type": "create_invoice",
        "expected_collected": {
            "customer_name": "Acme Corp",
            "amount": "5000",
            "currency": "EUR",
            "invoice_date": "2024-03-15",
            "description": "consulting services"
        },
        "expected_missing": [],
        "description": "Complete invoice request with all required fields"
    },

    "incomplete_invoice": {
        "query": "Create an invoice for €3000",
        "expected_action_type": "create_invoice",
        "expected_collected": {
            "amount": "3000",
            "currency": "EUR"
        },
        "expected_missing": ["customer_name", "invoice_date", "description"],
        "description": "Incomplete invoice - missing customer, date, and description"
    },

    "ambiguous_invoice": {
        "query": "I need to invoice someone",
        "expected_action_type": "create_invoice",
        "expected_collected": {},
        "expected_missing": ["customer_name", "amount", "invoice_date", "description"],
        "is_ambiguous": True,
        "description": "Very vague invoice request - almost everything missing"
    },

    "complete_quote": {
        "query": "Send a quote to john.doe@example.com for John Doe with 3 laptops and 2 monitors",
        "expected_action_type": "send_quote",
        "expected_collected": {
            "customer_email": "john.doe@example.com",
            "customer_name": "John Doe",
            "items": "3 laptops and 2 monitors"
        },
        "expected_missing": [],
        "description": "Complete quote request with all required fields"
    },

    "incomplete_quote": {
        "query": "I want to send a quote",
        "expected_action_type": "send_quote",
        "expected_collected": {},
        "expected_missing": ["customer_name", "customer_email", "items"],
        "description": "Incomplete quote - missing all required fields"
    },

    "quote_with_invalid_email": {
        "query": "Send a quote to john.doe for office supplies",
        "expected_action_type": "send_quote",
        "expected_collected": {
            "items": "office supplies"
        },
        "expected_missing": ["customer_email"],  # "john.doe" is not valid without @domain
        "description": "Quote with invalid email format"
    },

    "payment_status_with_id": {
        "query": "Check the status of payment PAY-12345",
        "expected_action_type": "check_payment_status",
        "expected_collected": {
            "payment_id": "PAY-12345"
        },
        "expected_missing": [],
        "description": "Payment status check with payment ID"
    },

    "payment_status_with_invoice": {
        "query": "What's the payment status for invoice INV-98765?",
        "expected_action_type": "check_payment_status",
        "expected_collected": {
            "invoice_id": "INV-98765"
        },
        "expected_missing": [],
        "description": "Payment status check with invoice ID"
    },

    "payment_status_vague": {
        "query": "Check payment status",
        "expected_action_type": "check_payment_status",
        "expected_collected": {},
        "expected_missing": ["payment_id", "invoice_id", "customer_name"],  # Need at least one
        "is_ambiguous": True,
        "description": "Vague payment check - no identifiers provided"
    },

    "payment_status_date_range": {
        "query": "Check payments from Acme Corp between 2024-01-01 and 2024-01-31",
        "expected_action_type": "check_payment_status",
        "expected_collected": {
            "customer_name": "Acme Corp",
            "date_from": "2024-01-01",
            "date_to": "2024-01-31"
        },
        "expected_missing": [],
        "description": "Payment status with customer name and date range"
    },

    "invoice_with_multiple_dates": {
        "query": "Create invoice for TechCorp €10000 on March 15, 2024, due April 15, 2024 for software license",
        "expected_action_type": "create_invoice",
        "expected_collected": {
            "customer_name": "TechCorp",
            "amount": "10000",
            "currency": "EUR",
            "invoice_date": "2024-03-15",
            "due_date": "2024-04-15",
            "description": "software license"
        },
        "expected_missing": [],
        "description": "Invoice with both invoice date and due date"
    },
}


def print_example(scenario_name: str):
    """Print a formatted example scenario."""
    scenario = EXAMPLE_SCENARIOS[scenario_name]

    print(f"\n{'='*70}")
    print(f"Scenario: {scenario_name}")
    print(f"{'='*70}")
    print(f"\nDescription: {scenario['description']}")
    print(f"\nUser Query:")
    print(f"  \"{scenario['query']}\"")
    print(f"\nExpected Action Type: {scenario['expected_action_type']}")

    print(f"\nExpected Collected Fields:")
    if scenario['expected_collected']:
        for key, value in scenario['expected_collected'].items():
            print(f"  - {key}: {value}")
    else:
        print("  (none)")

    print(f"\nExpected Missing Fields:")
    if scenario['expected_missing']:
        for field in scenario['expected_missing']:
            print(f"  - {field}")
    else:
        print("  (none)")

    if scenario.get('is_ambiguous'):
        print(f"\n⚠️  Expected to be flagged as AMBIGUOUS")

    print(f"\n{'='*70}\n")


def print_all_examples():
    """Print all example scenarios."""
    print("\n" + "="*70)
    print("CLARIFICATION AGENT - EXAMPLE SCENARIOS")
    print("="*70)

    for scenario_name in EXAMPLE_SCENARIOS.keys():
        print_example(scenario_name)


if __name__ == "__main__":
    # Print all examples when run directly
    print_all_examples()

