"""
Field validators for clarified user inputs.
Provides validation functions for common field types.
"""
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Tuple
import re


class ValidationResult:
    """Result of a field validation."""
    def __init__(self, is_valid: bool, normalized_value: Any = None, error_message: str = None):
        self.is_valid = is_valid
        self.normalized_value = normalized_value
        self.error_message = error_message


def validate_email(value: str) -> ValidationResult:
    """
    Validate email format.

    Args:
        value: Email string to validate

    Returns:
        ValidationResult with normalized lowercase email if valid
    """
    if not value or not isinstance(value, str):
        return ValidationResult(False, None, "Email is required")

    # Basic email pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(email_pattern, value):
        return ValidationResult(False, None, "Invalid email format. Expected format: name@domain.com")

    return ValidationResult(True, value.lower().strip())


def validate_date(value: str, field_name: str = "date") -> ValidationResult:
    """
    Validate and parse date string.
    Accepts multiple formats: YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY, etc.

    Args:
        value: Date string to validate
        field_name: Name of the field for error messages

    Returns:
        ValidationResult with normalized date in YYYY-MM-DD format if valid
    """
    if not value:
        return ValidationResult(False, None, f"{field_name} is required")

    # Try multiple date formats
    date_formats = [
        "%Y-%m-%d",      # 2024-03-15
        "%d/%m/%Y",      # 15/03/2024
        "%d-%m-%Y",      # 15-03-2024
        "%Y/%m/%d",      # 2024/03/15
        "%d.%m.%Y",      # 15.03.2024
        "%B %d, %Y",     # March 15, 2024
        "%d %B %Y",      # 15 March 2024
    ]

    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(str(value).strip(), fmt).date()
            # Normalize to YYYY-MM-DD
            return ValidationResult(True, parsed_date.strftime("%Y-%m-%d"))
        except ValueError:
            continue

    return ValidationResult(
        False,
        None,
        f"Invalid date format for {field_name}. Please use format: YYYY-MM-DD (e.g., 2024-03-15)"
    )


def validate_amount(value: str, min_value: float = 0.01, currency: str = None) -> ValidationResult:
    """
    Validate monetary amount.

    Args:
        value: Amount as string or number
        min_value: Minimum allowed value
        currency: Optional currency code for context

    Returns:
        ValidationResult with normalized Decimal value if valid
    """
    if not value:
        return ValidationResult(False, None, "Amount is required")

    try:
        # Remove common currency symbols and spaces
        cleaned = str(value).strip()
        cleaned = cleaned.replace('€', '').replace('$', '').replace('£', '').replace(' ', '')
        cleaned = cleaned.strip()

        # Handle different decimal separators
        # If both comma and dot present, comma is thousands separator
        if ',' in cleaned and '.' in cleaned:
            cleaned = cleaned.replace(',', '')
        # If only comma, it might be decimal separator (European format)
        elif ',' in cleaned:
            cleaned = cleaned.replace(',', '.')

        amount = Decimal(cleaned)

        if amount < Decimal(str(min_value)):
            return ValidationResult(
                False,
                None,
                f"Amount must be at least {min_value}{' ' + currency if currency else ''}"
            )

        # Normalize to 2 decimal places for currencies
        normalized = amount.quantize(Decimal('0.01'))
        return ValidationResult(True, str(normalized))

    except (InvalidOperation, ValueError):
        return ValidationResult(
            False,
            None,
            f"Invalid amount format. Expected a number (e.g., 1234.56)"
        )


def validate_currency(value: str) -> ValidationResult:
    """
    Validate currency code.

    Args:
        value: Currency code (e.g., EUR, USD, GBP)

    Returns:
        ValidationResult with normalized uppercase currency code if valid
    """
    valid_currencies = ["EUR", "USD", "GBP"]

    if not value:
        return ValidationResult(True, "EUR")  # Default to EUR

    normalized = value.strip().upper()

    if normalized not in valid_currencies:
        return ValidationResult(
            False,
            None,
            f"Invalid currency. Supported: {', '.join(valid_currencies)}"
        )

    return ValidationResult(True, normalized)


def validate_required_text(value: str, field_name: str = "field", min_length: int = 1) -> ValidationResult:
    """
    Validate required text field.

    Args:
        value: Text value to validate
        field_name: Name of the field for error messages
        min_length: Minimum required length

    Returns:
        ValidationResult with trimmed text if valid
    """
    if not value or not isinstance(value, str):
        return ValidationResult(False, None, f"{field_name} is required")

    trimmed = value.strip()

    if len(trimmed) < min_length:
        return ValidationResult(
            False,
            None,
            f"{field_name} must be at least {min_length} character(s)"
        )

    return ValidationResult(True, trimmed)


def validate_collected_fields(collected_fields: dict, action_type: str) -> Tuple[dict, list]:
    """
    Validate all collected fields for a specific action type.

    Args:
        collected_fields: Dictionary of field_name -> value
        action_type: Type of action (e.g., "create_invoice")

    Returns:
        Tuple of (validated_fields dict, list of error messages)
    """
    validated = {}
    errors = []

    if action_type == "create_invoice":
        # Validate customer_name
        if "customer_name" in collected_fields:
            result = validate_required_text(collected_fields["customer_name"], "Customer name")
            if result.is_valid:
                validated["customer_name"] = result.normalized_value
            else:
                errors.append(result.error_message)

        # Validate amount
        if "amount" in collected_fields:
            currency = collected_fields.get("currency", "EUR")
            result = validate_amount(collected_fields["amount"], min_value=0.01, currency=currency)
            if result.is_valid:
                validated["amount"] = result.normalized_value
            else:
                errors.append(result.error_message)

        # Validate dates
        if "invoice_date" in collected_fields:
            result = validate_date(collected_fields["invoice_date"], "Invoice date")
            if result.is_valid:
                validated["invoice_date"] = result.normalized_value
            else:
                errors.append(result.error_message)

        if "due_date" in collected_fields:
            result = validate_date(collected_fields["due_date"], "Due date")
            if result.is_valid:
                validated["due_date"] = result.normalized_value
            else:
                errors.append(result.error_message)

        # Validate currency
        if "currency" in collected_fields:
            result = validate_currency(collected_fields["currency"])
            if result.is_valid:
                validated["currency"] = result.normalized_value
            else:
                errors.append(result.error_message)

    elif action_type == "send_quote":
        # Validate customer_name
        if "customer_name" in collected_fields:
            result = validate_required_text(collected_fields["customer_name"], "Customer name")
            if result.is_valid:
                validated["customer_name"] = result.normalized_value
            else:
                errors.append(result.error_message)

        # Validate email
        if "customer_email" in collected_fields:
            result = validate_email(collected_fields["customer_email"])
            if result.is_valid:
                validated["customer_email"] = result.normalized_value
            else:
                errors.append(result.error_message)

        # Validate amount if provided
        if "total_amount" in collected_fields:
            currency = collected_fields.get("currency", "EUR")
            result = validate_amount(collected_fields["total_amount"], min_value=0.01, currency=currency)
            if result.is_valid:
                validated["total_amount"] = result.normalized_value
            else:
                errors.append(result.error_message)

    elif action_type == "check_payment_status":
        # Validate dates if provided
        if "date_from" in collected_fields:
            result = validate_date(collected_fields["date_from"], "Start date")
            if result.is_valid:
                validated["date_from"] = result.normalized_value
            else:
                errors.append(result.error_message)

        if "date_to" in collected_fields:
            result = validate_date(collected_fields["date_to"], "End date")
            if result.is_valid:
                validated["date_to"] = result.normalized_value
            else:
                errors.append(result.error_message)

    # Copy over non-validated fields as-is
    for key, value in collected_fields.items():
        if key not in validated:
            validated[key] = value

    return validated, errors



