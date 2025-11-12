import pytest
from decimal import Decimal
from app.services.rate_service import RateService


class TestRateService:
    """Test Rate Service functionality"""

    def test_get_direct_rate(self, app):
        """Test getting direct exchange rate"""
        with app.app_context():
            rate = RateService.get_rate('USD', 'KES')
            assert rate > 0
            assert isinstance(rate, Decimal)

    def test_get_inverse_rate(self, app):
        """Test getting inverse rate"""
        with app.app_context():
            # Get USD/KES
            usd_kes = RateService.get_rate('USD', 'KES')

            # Get KES/USD (inverse)
            kes_usd = RateService.get_rate('KES', 'USD')

            # Verify inverse relationship
            assert abs(usd_kes * kes_usd - Decimal('1')) < Decimal('0.0001')

    def test_get_cross_rate(self, app):
        """Test cross rate calculation"""
        with app.app_context():
            # Get cross rate KES/NGN
            kes_ngn = RateService.get_rate('KES', 'NGN')

            assert kes_ngn > 0
            assert isinstance(kes_ngn, Decimal)

    def test_set_rate(self, app):
        """Test setting exchange rate"""
        with app.app_context():
            new_rate = RateService.set_rate('USD', 'GBP', '0.79')

            assert new_rate == Decimal('0.79')

            # Verify we can retrieve it
            retrieved_rate = RateService.get_rate('USD', 'GBP')
            assert retrieved_rate == Decimal('0.79')

    def test_update_existing_rate(self, app):
        """Test updating an existing rate"""
        with app.app_context():
            # Set initial rate
            RateService.set_rate('USD', 'KES', '130.00')

            # Update rate
            RateService.set_rate('USD', 'KES', '131.00')

            # Verify update
            rate = RateService.get_rate('USD', 'KES')
            assert rate == Decimal('131.00')

    def test_get_all_rates(self, app):
        """Test getting all rates"""
        with app.app_context():
            rates = RateService.get_all_rates()

            assert len(rates) > 0
            assert all('base_currency' in r for r in rates)
            assert all('target_currency' in r for r in rates)
            assert all('rate' in r for r in rates)

    def test_nonexistent_rate(self, app):
        """Test getting non-existent rate"""
        with app.app_context():
            with pytest.raises(ValueError, match="No exchange rate available"):
                RateService.get_rate('XXX', 'YYY')