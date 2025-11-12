from datetime import datetime
from flask import current_app
from app import db
from app.models.quote import Quote
from app.models.transaction import Transaction
from app.services.rate_service import RateService
from app.utils.decimal_utils import to_decimal, round_currency, calculate_spread
from app.utils.validators import validate_currency_pair, validate_amount


class FXService:
    """Service for FX operations - quotes and transactions"""

    @staticmethod
    def generate_quote(from_currency, to_currency, amount):
        """
        Generate an FX quote

        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            amount: Amount to convert

        Returns:
            Quote object
        """
        # Validate inputs
        validate_currency_pair(from_currency, to_currency)
        amount_decimal = validate_amount(amount)

        # Get base exchange rate
        base_rate = RateService.get_rate(from_currency, to_currency)

        # Apply spread (customer pays spread on conversion)
        buy_spread_bps = current_app.config['BUY_SPREAD_BPS']
        rate_with_spread = calculate_spread(base_rate, buy_spread_bps, is_buy=True)

        # Calculate target amount
        converted_amount = amount_decimal * rate_with_spread
        converted_amount_rounded = round_currency(converted_amount)

        # Create quote
        quote = Quote(
            from_currency=from_currency,
            to_currency=to_currency,
            from_amount=amount_decimal,
            to_amount=converted_amount_rounded,
            exchange_rate=rate_with_spread
        )

        db.session.add(quote)
        db.session.commit()

        return quote

    @staticmethod
    def execute_quote(quote_id, idempotency_key=None):
        """
        Execute a quote to create a transaction

        Args:
            quote_id: ID of the quote to execute
            idempotency_key: Optional key to prevent duplicate executions

        Returns:
            Transaction object
        """
        # Fetch quote with row-level locking to prevent race conditions
        quote = db.session.query(Quote).filter_by(id=quote_id).with_for_update().first()

        if not quote:
            raise ValueError(f"Quote {quote_id} not found")

        # Check if already executed (idempotency)
        if quote.is_executed:
            # Return existing transaction
            transaction = Transaction.query.filter_by(quote_id=quote_id).first()
            if transaction:
                return transaction
            raise ValueError(f"Quote {quote_id} was already executed but transaction not found")

        # Validate quote is not expired
        if quote.is_expired():
            raise ValueError(f"Quote {quote_id} has expired")

        # Create transaction
        transaction = Transaction(
            quote_id=quote.id,
            from_currency=quote.from_currency,
            to_currency=quote.to_currency,
            from_amount=quote.from_amount,
            to_amount=quote.to_amount,
            exchange_rate=quote.exchange_rate,
            status='completed'
        )

        # Mark quote as executed
        quote.is_executed = True
        quote.executed_at = datetime.utcnow()

        db.session.add(transaction)
        db.session.commit()

        return transaction

    @staticmethod
    def get_quote(quote_id):
        """Retrieve a quote by ID"""
        quote = Quote.query.get(quote_id)
        if not quote:
            raise ValueError(f"Quote {quote_id} not found")
        return quote

    @staticmethod
    def get_transaction(transaction_id):
        """Retrieve a transaction by ID"""
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            raise ValueError(f"Transaction {transaction_id} not found")
        return transaction

    @staticmethod
    def get_transaction_history(limit=100):
        """Get recent transaction history"""
        transactions = Transaction.query.order_by(
            Transaction.created_at.desc()
        ).limit(limit).all()

        return [t.to_dict() for t in transactions]