from flask import current_app
from decimal import Decimal


def validate_currency(currency):
    """Validate if currency is supported"""
    supported = current_app.config['SUPPORTED_CURRENCIES']
    if currency not in supported:
        raise ValueError(f"Unsupported currency: {currency}. Supported: {', '.join(supported)}")
    return True


def validate_amount(amount):
    """Validate amount is positive and valid"""
    try:
        decimal_amount = Decimal(str(amount))
        if decimal_amount <= 0:
            raise ValueError("Amount must be greater than zero")
        return decimal_amount
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid amount: {amount}")


def validate_currency_pair(from_currency, to_currency):
    """Validate currency pair"""
    validate_currency(from_currency)
    validate_currency(to_currency)

    if from_currency == to_currency:
        raise ValueError("Source and target currencies must be different")

    return True