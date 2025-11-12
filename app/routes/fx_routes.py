from flask import Blueprint, request, jsonify
from app.services.fx_service import FXService
from app.services.rate_service import RateService

fx_bp = Blueprint('fx', __name__)


@fx_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'FX Engine'}), 200


@fx_bp.route('/quotes', methods=['POST'])
def create_quote():
    """
    Generate FX quote

    Request body:
    {
        "from_currency": "USD",
        "to_currency": "KES",
        "amount": "100.00"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        from_currency = data.get('from_currency')
        to_currency = data.get('to_currency')
        amount = data.get('amount')

        if not all([from_currency, to_currency, amount]):
            return jsonify({
                'error': 'Missing required fields: from_currency, to_currency, amount'
            }), 400

        quote = FXService.generate_quote(from_currency, to_currency, amount)

        return jsonify({
            'success': True,
            'data': quote.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@fx_bp.route('/quotes/<quote_id>', methods=['GET'])
def get_quote(quote_id):
    """Get quote by ID"""
    try:
        quote = FXService.get_quote(quote_id)
        return jsonify({
            'success': True,
            'data': quote.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@fx_bp.route('/transactions', methods=['POST'])
def execute_transaction():
    """
    Execute FX transaction from quote

    Request body:
    {
        "quote_id": "uuid-here",
        "idempotency_key": "optional-key"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        quote_id = data.get('quote_id')
        idempotency_key = data.get('idempotency_key')

        if not quote_id:
            return jsonify({'error': 'Missing required field: quote_id'}), 400

        transaction = FXService.execute_quote(quote_id, idempotency_key)

        return jsonify({
            'success': True,
            'data': transaction.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@fx_bp.route('/transactions/<transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """Get transaction by ID"""
    try:
        transaction = FXService.get_transaction(transaction_id)
        return jsonify({
            'success': True,
            'data': transaction.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@fx_bp.route('/transactions', methods=['GET'])
def get_transaction_history():
    """Get transaction history"""
    try:
        limit = request.args.get('limit', 100, type=int)
        transactions = FXService.get_transaction_history(limit)

        return jsonify({
            'success': True,
            'data': transactions,
            'count': len(transactions)
        }), 200

    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@fx_bp.route('/rates', methods=['GET'])
def get_all_rates():
    """Get all exchange rates"""
    try:
        rates = RateService.get_all_rates()
        return jsonify({
            'success': True,
            'data': rates
        }), 200

    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@fx_bp.route('/rates/update', methods=['POST'])
def update_rates():
    """
    Update exchange rates from external API

    Request body (optional):
    {
        "base_currency": "USD"
    }
    """
    try:
        data = request.get_json() or {}
        base_currency = data.get('base_currency', 'USD')

        result = RateService.update_rates_from_api(base_currency)

        return jsonify({
            'success': True,
            'data': result
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@fx_bp.route('/rates', methods=['POST'])
def set_rate():
    """
    Manually set exchange rate

    Request body:
    {
        "base_currency": "USD",
        "target_currency": "KES",
        "rate": "129.50"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        base_currency = data.get('base_currency')
        target_currency = data.get('target_currency')
        rate = data.get('rate')

        if not all([base_currency, target_currency, rate]):
            return jsonify({
                'error': 'Missing required fields: base_currency, target_currency, rate'
            }), 400

        updated_rate = RateService.set_rate(base_currency, target_currency, rate)

        return jsonify({
            'success': True,
            'data': {
                'base_currency': base_currency,
                'target_currency': target_currency,
                'rate': str(updated_rate)
            }
        }), 201

    except ValueError as e:
        print("ValueError: ", e)
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print("Exception: ", e)
        return jsonify({'error': 'Internal server error'}), 500
