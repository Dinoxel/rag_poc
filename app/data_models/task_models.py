"""
Task-specific data models for business actions.
Each model represents a specific action that can be executed by the system.

NOTE: These models are defined locally for POC purposes.
In production, if these models are managed by an external API backend,
we should either:
  1. Generate these models from OpenAPI/Swagger specs
  2. Keep them synchronized with the backend schema
  3. Use a shared schema repository
See README for more details on model governance.
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from decimal import Decimal


class InvoiceCreationTask(BaseModel):
    """Model for creating an invoice."""

    customer_name: str = Field(description="Name of the customer")
    customer_id: Optional[str] = Field(default=None, description="Customer ID if available")

    amount: Decimal = Field(description="Invoice amount", gt=0)
    currency: Literal["EUR", "USD", "GBP"] = Field(default="EUR", description="Currency code")

    invoice_date: date = Field(description="Invoice date")
    due_date: Optional[date] = Field(default=None, description="Payment due date")

    description: str = Field(description="Invoice description/items")
    reference: Optional[str] = Field(default=None, description="Invoice reference number")

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v, info):
        if v and info.data.get('invoice_date'):
            if v < info.data['invoice_date']:
                raise ValueError("Due date cannot be before invoice date")
        return v


class QuoteSendTask(BaseModel):
    """Model for sending a quote/devis."""

    customer_name: str = Field(description="Name of the customer")
    customer_email: str = Field(description="Customer email address")
    customer_id: Optional[str] = Field(default=None, description="Customer ID if available")

    items: str = Field(description="Description of items/services to quote")
    total_amount: Optional[Decimal] = Field(default=None, description="Total quote amount", gt=0)

    valid_until: Optional[date] = Field(default=None, description="Quote validity date")
    currency: Literal["EUR", "USD", "GBP"] = Field(default="EUR", description="Currency code")

    notes: Optional[str] = Field(default=None, description="Additional notes for the quote")

    @field_validator('customer_email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v or '.' not in v.split('@')[-1]:
            raise ValueError("Invalid email format")
        return v.lower()


class PaymentStatusTask(BaseModel):
    """Model for checking payment status."""

    payment_id: Optional[str] = Field(default=None, description="Payment/transaction ID")
    invoice_id: Optional[str] = Field(default=None, description="Invoice ID")
    customer_name: Optional[str] = Field(default=None, description="Customer name")

    date_from: Optional[date] = Field(default=None, description="Start date for search period")
    date_to: Optional[date] = Field(default=None, description="End date for search period")

    @field_validator('invoice_id', 'payment_id')
    @classmethod
    def at_least_one_id(cls, v, info):
        # If neither payment_id, invoice_id, nor customer_name is provided, raise error
        # This validation happens after all fields are set
        return v

    def model_post_init(self, __context):
        """Ensure at least one identifier is provided."""
        if not any([self.payment_id, self.invoice_id, self.customer_name]):
            raise ValueError("At least one of payment_id, invoice_id, or customer_name must be provided")


# Registry mapping action types to their models
TASK_MODEL_REGISTRY = {
    "create_invoice": InvoiceCreationTask,
    "send_quote": QuoteSendTask,
    "check_payment_status": PaymentStatusTask,
}


def get_task_model(action_type: str):
    """Get the appropriate task model for an action type."""
    return TASK_MODEL_REGISTRY.get(action_type)

