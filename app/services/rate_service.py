import requests
from datetime import datetime, timedelta
from decimal import Decimal
from flask import current_app
from app import db
from app.models.exchange_rate import ExchangeRate
from app.utils.decimal_utils import to_decimal, safe_divide


class RateService:
    """Service for managing exchange rates"""

    @staticmethod
    def get_rate(from_currency, to_currency):
        """
        Get exchange rate between two currencies
        Returns the rate with spread applied
        """
        # Check if it's a direct rate
        rate = ExchangeRate.query.filter_by(
            base_currency=from_currency,
            target_currency=to_currency
        ).first()

        if rate:
            return to_decimal(rate.rate)

        # Check if inverse rate exists
        inverse_rate = ExchangeRate.query.filter_by(
            base_currency=to_currency,
            target_currency=from_currency
        ).first()

        if inverse_rate:
            # Calculate inverse: if EUR/USD = 1.1, then USD/EUR = 1/1.1
            return safe_divide(Decimal('1'), to_decimal(inverse_rate.rate))

        # Try to calculate cross rate (e.g., KES/NGN through USD)
        cross_rate = RateService._calculate_cross_rate(from_currency, to_currency)
        if cross_rate:
            return cross_rate

        raise ValueError(f"No exchange rate available for {from_currency}/{to_currency}")

    @staticmethod
    def _calculate_cross_rate(from_currency, to_currency):
        """
        Calculate cross rate through a common currency (USD)
        E.g., KES/NGN = (KES/USD) * (USD/NGN)
        """
        if from_currency == 'USD' or to_currency == 'USD':
            return None

        try:
            # Get rates to/from USD
            from_to_usd = RateService.get_rate(from_currency, 'USD')
            usd_to_target = RateService.get_rate('USD', to_currency)

            # Calculate cross rate
            return from_to_usd * usd_to_target
        except ValueError:
            return None

    @staticmethod
    def update_rates_from_api(base_currency='USD'):
        """
        Fetch latest rates from external API
        """
        api_url = current_app.config['EXCHANGE_RATE_API_URL']

        try:
            response = requests.get(f"{api_url}{base_currency}", timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'rates' not in data:
                raise ValueError("Invalid API response format")

            rates_updated = 0
            supported_currencies = current_app.config['SUPPORTED_CURRENCIES']

            for currency, rate in data['rates'].items():
                if currency in supported_currencies and currency != base_currency:
                    RateService.set_rate(base_currency, currency, rate)
                    rates_updated += 1

            return {
                'success': True,
                'rates_updated': rates_updated,
                'base_currency': base_currency,
                'timestamp': datetime.utcnow().isoformat()
            }

        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch rates from API: {str(e)}")

    @staticmethod
    def set_rate(base_currency, target_currency, rate):
        """
        Set or update exchange rate
        """
        rate_decimal = to_decimal(rate)

        # Check if rate exists
        existing_rate = ExchangeRate.query.filter_by(
            base_currency=base_currency,
            target_currency=target_currency
        ).first()

        if existing_rate:
            existing_rate.rate = rate_decimal
            existing_rate.updated_at = datetime.utcnow()
        else:
            new_rate = ExchangeRate(
                base_currency=base_currency,
                target_currency=target_currency,
                rate=rate_decimal
            )
            db.session.add(new_rate)

        db.session.commit()
        return rate_decimal

    @staticmethod
    def get_all_rates():
        """Get all stored exchange rates"""
        rates = ExchangeRate.query.all()
        return [rate.to_dict() for rate in rates]

    @staticmethod
    def is_rate_stale(from_currency, to_currency):
        """Check if rate is stale (older than threshold)"""
        rate = ExchangeRate.query.filter_by(
            base_currency=from_currency,
            target_currency=to_currency
        ).first()

        if not rate:
            return True

        threshold_hours = current_app.config['RATE_STALENESS_THRESHOLD_HOURS']
        threshold = datetime.utcnow() - timedelta(hours=threshold_hours)

        return rate.updated_at < threshold

    @staticmethod
    def seed_initial_rates():
        """Seed database with initial rates for testing"""
        initial_rates = {
            'USD': {'EUR': '0.92', 'KES': '129.50', 'NGN': '775.00'},
            'EUR': {'USD': '1.09', 'KES': '140.76', 'NGN': '842.39'},
        }

        for base, targets in initial_rates.items():
            for target, rate in targets.items():
                RateService.set_rate(base, target, rate)

        return True