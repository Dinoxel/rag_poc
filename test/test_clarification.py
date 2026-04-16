"""
Quick test script to verify the clarification system components.
Run this to check if all models and validators are working correctly.
"""
from app.data_models.models import MissingField, ClarifyOutput
from app.data_models.task_models import InvoiceCreationTask, QuoteSendTask, PaymentStatusTask
from app.tools.field_validators import (
    validate_email,
    validate_date,
    validate_amount,
    validate_currency,
    validate_collected_fields
)
from datetime import date


def test_models():
    """Test that all Pydantic models can be instantiated."""
    print("🧪 Testing Pydantic models...")

    # Test MissingField
    missing = MissingField(
        field_name="customer_email",
        question="What is the customer's email?",
        field_type="email",
        is_required=True,
        validation_hint="Format: name@domain.com"
    )
    assert missing.field_name == "customer_email"
    print("✅ MissingField model OK")

    # Test ClarifyOutput
    clarify = ClarifyOutput(
        action_type="create_invoice",
        collected_fields={"amount": "5000"},
        missing_fields=[missing],
        confidence_score=0.8
    )
    assert clarify.action_type == "create_invoice"
    print("✅ ClarifyOutput model OK")

    # Test InvoiceCreationTask
    invoice = InvoiceCreationTask(
        customer_name="Acme Corp",
        amount=5000.00,
        invoice_date=date(2024, 3, 15),
        description="Consulting services"
    )
    assert invoice.customer_name == "Acme Corp"
    print("✅ InvoiceCreationTask model OK")

    # Test QuoteSendTask
    quote = QuoteSendTask(
        customer_name="Tech Inc",
        customer_email="contact@techinc.com",
        items="3 laptops"
    )
    assert quote.customer_email == "contact@techinc.com"
    print("✅ QuoteSendTask model OK")

    # Test PaymentStatusTask
    payment = PaymentStatusTask(
        payment_id="PAY-12345"
    )
    assert payment.payment_id == "PAY-12345"
    print("✅ PaymentStatusTask model OK")

    print("\n✅ All Pydantic models working correctly!\n")


def test_validators():
    """Test field validators."""
    print("🧪 Testing field validators...")

    # Test email validator
    result = validate_email("john@example.com")
    assert result.is_valid
    assert result.normalized_value == "john@example.com"
    print("✅ Email validator OK")

    # Test invalid email
    result = validate_email("invalid-email")
    assert not result.is_valid
    print("✅ Email validator rejects invalid format")

    # Test date validator
    result = validate_date("2024-03-15", "test_date")
    assert result.is_valid
    assert result.normalized_value == "2024-03-15"
    print("✅ Date validator OK (YYYY-MM-DD)")

    # Test alternate date format
    result = validate_date("15/03/2024", "test_date")
    assert result.is_valid
    assert result.normalized_value == "2024-03-15"
    print("✅ Date validator OK (DD/MM/YYYY)")

    # Test amount validator
    result = validate_amount("5000.50", currency="EUR")
    assert result.is_valid
    assert result.normalized_value == "5000.50"
    print("✅ Amount validator OK")

    # Test amount with currency symbol
    result = validate_amount("€1,234.56")
    assert result.is_valid
    assert result.normalized_value == "1234.56"
    print("✅ Amount validator handles currency symbols")

    # Test currency validator
    result = validate_currency("eur")
    assert result.is_valid
    assert result.normalized_value == "EUR"
    print("✅ Currency validator OK")

    # Test invalid currency
    result = validate_currency("JPY")
    assert not result.is_valid
    print("✅ Currency validator rejects unsupported currencies")

    print("\n✅ All validators working correctly!\n")


def test_field_validation_integration():
    """Test integrated field validation for different action types."""
    print("🧪 Testing integrated field validation...")

    # Test invoice validation
    invoice_fields = {
        "customer_name": "Acme Corp",
        "amount": "5000",
        "currency": "eur",
        "invoice_date": "15/03/2024",
        "description": "Services"
    }

    validated, errors = validate_collected_fields(invoice_fields, "create_invoice")
    assert len(errors) == 0, f"Unexpected errors: {errors}"
    assert validated["currency"] == "EUR"  # Normalized
    assert validated["invoice_date"] == "2024-03-15"  # Normalized
    assert validated["amount"] == "5000.00"  # Normalized
    print("✅ Invoice field validation OK")

    # Test quote validation
    quote_fields = {
        "customer_name": "Tech Inc",
        "customer_email": "Contact@TechInc.COM",
        "items": "Laptops"
    }

    validated, errors = validate_collected_fields(quote_fields, "send_quote")
    assert len(errors) == 0
    assert validated["customer_email"] == "contact@techinc.com"  # Normalized to lowercase
    print("✅ Quote field validation OK")

    # Test validation with errors
    bad_fields = {
        "customer_name": "Test",
        "customer_email": "not-an-email",
        "items": "Something"
    }

    validated, errors = validate_collected_fields(bad_fields, "send_quote")
    assert len(errors) > 0  # Should have email validation error
    print(f"✅ Validation correctly catches errors: {len(errors)} error(s)")

    print("\n✅ Integrated field validation working correctly!\n")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print("CLARIFICATION SYSTEM - COMPONENT TESTS")
    print("="*70 + "\n")

    try:
        test_models()
        test_validators()
        test_field_validation_integration()

        print("="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print("\nThe clarification system is ready to use.")
        print("You can now test it with the main graph.")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()

