from flask import current_app
from decimal import Decimal, InvalidOperation


def validate_currency(currency):
    """Validate if currency is supported"""
    supported = current_app.config['SUPPORTED_CURRENCIES']
    if currency not in supported:
        raise ValueError(f"Unsupported currency: {currency}. Supported: {', '.join(supported)}")
    return True


def validate_amount(amount):
    """Validate that the amount is a valid positive decimal number."""
    try:
        # Convert safely to Decimal
        decimal_amount = Decimal(str(amount))
    except (InvalidOperation, TypeError):
        raise ValueError(f"Invalid amount: {amount}")

    # Check that it's greater than zero
    if decimal_amount <= 0:
        raise ValueError("Amount must be greater than zero")

    return decimal_amount


def validate_currency_pair(from_currency, to_currency):
    """Validate currency pair"""
    validate_currency(from_currency)
    validate_currency(to_currency)

    if from_currency == to_currency:
        raise ValueError("Source and target currencies must be different")

    return True
