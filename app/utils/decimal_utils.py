from decimal import Decimal, ROUND_HALF_UP, getcontext

# Set decimal precision for financial calculations
getcontext().prec = 28


def to_decimal(value):
    """Convert value to Decimal safely"""
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float, str)):
        return Decimal(str(value))
    raise ValueError(f"Cannot convert {type(value)} to Decimal")


def round_currency(amount, decimal_places=2):
    """Round amount to specified decimal places using banker's rounding"""
    if not isinstance(amount, Decimal):
        amount = to_decimal(amount)

    quantize_value = Decimal('0.1') ** decimal_places
    return amount.quantize(quantize_value, rounding=ROUND_HALF_UP)


def calculate_spread(rate, spread_bps, is_buy=True):
    """
    Calculate rate with spread applied

    Args:
        rate: Base exchange rate
        spread_bps: Spread in basis points (100 bps = 1%)
        is_buy: True for buy rate (add spread), False for sell rate (subtract spread)

    Returns:
        Decimal: Rate with spread applied
    """
    rate = to_decimal(rate)
    spread_bps = to_decimal(spread_bps)

    # Convert basis points to decimal (50 bps = 0.005 = 0.5%)
    spread_decimal = spread_bps / Decimal('10000')

    if is_buy:
        # For buying, we add the spread (customer pays more)
        return rate * (Decimal('1') + spread_decimal)
    else:
        # For selling, we subtract the spread (customer receives less)
        return rate * (Decimal('1') - spread_decimal)


def safe_divide(numerator, denominator):
    """Safely divide two numbers with Decimal precision"""
    numerator = to_decimal(numerator)
    denominator = to_decimal(denominator)

    if denominator == 0:
        raise ValueError("Cannot divide by zero")

    return numerator / denominator