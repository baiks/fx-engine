import uuid
from datetime import datetime, timedelta
from app import db
from flask import current_app


class Quote(db.Model):
    """Store FX quotes with expiration"""
    __tablename__ = 'quotes'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    from_currency = db.Column(db.String(3), nullable=False)
    to_currency = db.Column(db.String(3), nullable=False)
    from_amount = db.Column(db.Numeric(precision=18, scale=2), nullable=False)
    to_amount = db.Column(db.Numeric(precision=18, scale=2), nullable=False)
    exchange_rate = db.Column(db.Numeric(precision=18, scale=8), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_executed = db.Column(db.Boolean, default=False, nullable=False)
    executed_at = db.Column(db.DateTime, nullable=True)

    def __init__(self, **kwargs):
        super(Quote, self).__init__(**kwargs)
        if not self.expires_at:
            validity_seconds = current_app.config['QUOTE_VALIDITY_SECONDS']
            self.expires_at = datetime.utcnow() + timedelta(seconds=validity_seconds)

    def is_valid(self):
        """Check if quote is still valid (not expired and not executed)"""
        return not self.is_executed and datetime.utcnow() < self.expires_at

    def is_expired(self):
        """Check if quote has expired"""
        return datetime.utcnow() >= self.expires_at

    def to_dict(self):
        return {
            'quote_id': self.id,
            'from_currency': self.from_currency,
            'to_currency': self.to_currency,
            'from_amount': str(self.from_amount),
            'to_amount': str(self.to_amount),
            'exchange_rate': str(self.exchange_rate),
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'is_executed': self.is_executed,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None
        }

    def __repr__(self):
        return f'<Quote {self.id}: {self.from_currency}->{self.to_currency}>'