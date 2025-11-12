import pytest
from decimal import Decimal
from app.services.fx_service import FXService
from app.services.rate_service import RateService


class TestFXService:
    """Test FX Service functionality"""

    def test_generate_quote(self, app):
        """Test quote generation"""
        with app.app_context():
            quote = FXService.generate_quote('USD', 'KES', '100')

            assert quote is not None
            assert quote.from_currency == 'USD'
            assert quote.to_currency == 'KES'
            assert quote.from_amount == Decimal('100.00')
            assert quote.to_amount > 0
            assert quote.exchange_rate > 0
            assert not quote.is_executed
            assert quote.is_valid()

    def test_quote_with_spread(self, app):
        """Test that quotes include spread"""
        with app.app_context():
            # Get base rate
            base_rate = RateService.get_rate('USD', 'KES')

            # Generate quote
            quote = FXService.generate_quote('USD', 'KES', '100')

            # Quote rate should be higher than base rate (buy spread)
            assert quote.exchange_rate > base_rate

    def test_invalid_currency(self, app):
        """Test quote generation with invalid currency"""
        with app.app_context():
            with pytest.raises(ValueError, match="Unsupported currency"):
                FXService.generate_quote('USD', 'XXX', '100')

    def test_invalid_amount(self, app):
        """Test quote generation with invalid amount"""
        with app.app_context():
            with pytest.raises(ValueError, match="Amount must be greater than zero"):
                FXService.generate_quote('USD', 'KES', '-100')

            with pytest.raises(ValueError, match="Amount must be greater than zero"):
                FXService.generate_quote('USD', 'KES', '0')

    def test_same_currency(self, app):
        """Test quote generation with same source and target"""
        with app.app_context():
            with pytest.raises(ValueError, match="must be different"):
                FXService.generate_quote('USD', 'USD', '100')

    def test_execute_quote(self, app):
        """Test quote execution"""
        with app.app_context():
            # Generate quote
            quote = FXService.generate_quote('USD', 'KES', '100')
            quote_id = quote.id

            # Execute quote
            transaction = FXService.execute_quote(quote_id)

            assert transaction is not None
            assert transaction.quote_id == quote_id
            assert transaction.from_currency == 'USD'
            assert transaction.to_currency == 'KES'
            assert transaction.status == 'completed'

            # Verify quote is marked as executed
            updated_quote = FXService.get_quote(quote_id)
            assert updated_quote.is_executed
            assert not updated_quote.is_valid()

    def test_execute_quote_twice_idempotent(self, app):
        """Test that executing a quote twice returns same transaction (idempotency)"""
        with app.app_context():
            # Generate and execute quote
            quote = FXService.generate_quote('USD', 'KES', '100')
            transaction1 = FXService.execute_quote(quote.id)

            # Try to execute again
            transaction2 = FXService.execute_quote(quote.id)

            # Should return the same transaction
            assert transaction1.id == transaction2.id

    def test_execute_expired_quote(self, app):
        """Test that expired quotes cannot be executed"""
        with app.app_context():
            from datetime import datetime, timedelta
            from app.models.quote import Quote
            from app import db

            # Create an expired quote manually
            quote = Quote(
                from_currency='USD',
                to_currency='KES',
                from_amount=Decimal('100'),
                to_amount=Decimal('12950'),
                exchange_rate=Decimal('129.50')
            )
            # Force expiration
            quote.expires_at = datetime.utcnow() - timedelta(seconds=1)
            db.session.add(quote)
            db.session.commit()

            # Try to execute
            with pytest.raises(ValueError, match="expired"):
                FXService.execute_quote(quote.id)

    def test_execute_nonexistent_quote(self, app):
        """Test executing non-existent quote"""
        with app.app_context():
            with pytest.raises(ValueError, match="not found"):
                FXService.execute_quote('non-existent-id')

    def test_decimal_precision(self, app):
        """Test that decimal calculations are precise"""
        with app.app_context():
            quote = FXService.generate_quote('USD', 'KES', '100.33')

            # Verify amounts are Decimal type
            assert isinstance(quote.from_amount, Decimal)
            assert isinstance(quote.to_amount, Decimal)
            assert isinstance(quote.exchange_rate, Decimal)

            # Verify calculation precision
            calculated = quote.from_amount * quote.exchange_rate
            # Allow for rounding difference
            assert abs(calculated - quote.to_amount) < Decimal('0.01')

    def test_cross_rate_calculation(self, app):
        """Test cross rate calculation (e.g., KES to NGN)"""
        with app.app_context():
            quote = FXService.generate_quote('KES', 'NGN', '1000')

            assert quote is not None
            assert quote.to_amount > 0
            # KES is worth less than NGN, so should get fewer NGN
            assert quote.to_amount > Decimal('1')