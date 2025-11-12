from datetime import datetime
from app import db
from sqlalchemy import Index


class ExchangeRate(db.Model):
    """Store exchange rates with timestamp"""
    __tablename__ = 'exchange_rates'

    id = db.Column(db.Integer, primary_key=True)
    base_currency = db.Column(db.String(3), nullable=False)
    target_currency = db.Column(db.String(3), nullable=False)
    rate = db.Column(db.Numeric(precision=18, scale=8), nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Add composite index for efficient lookups
    __table_args__ = (
        Index('idx_currency_pair', 'base_currency', 'target_currency'),
    )

    def __repr__(self):
        return f'<ExchangeRate {self.base_currency}/{self.target_currency}: {self.rate}>'

    def to_dict(self):
        return {
            'id': self.id,
            'base_currency': self.base_currency,
            'target_currency': self.target_currency,
            'rate': str(self.rate),
            'updated_at': self.updated_at.isoformat()
        }