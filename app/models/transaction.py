import uuid
from datetime import datetime
from app import db


class Transaction(db.Model):
    """Store executed FX transactions for audit trail"""
    __tablename__ = 'transactions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quote_id = db.Column(db.String(36), db.ForeignKey('quotes.id'), nullable=False)
    from_currency = db.Column(db.String(3), nullable=False)
    to_currency = db.Column(db.String(3), nullable=False)
    from_amount = db.Column(db.Numeric(precision=18, scale=2), nullable=False)
    to_amount = db.Column(db.Numeric(precision=18, scale=2), nullable=False)
    exchange_rate = db.Column(db.Numeric(precision=18, scale=8), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='completed')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationship
    quote = db.relationship('Quote', backref='transaction', lazy=True)

    def to_dict(self):
        return {
            'transaction_id': self.id,
            'quote_id': self.quote_id,
            'from_currency': self.from_currency,
            'to_currency': self.to_currency,
            'from_amount': str(self.from_amount),
            'to_amount': str(self.to_amount),
            'exchange_rate': str(self.exchange_rate),
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<Transaction {self.id}: {self.from_currency}->{self.to_currency}>'