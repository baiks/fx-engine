import pytest
import json


class TestAPI:
    """Test API endpoints"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/v1/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'

    def test_create_quote_success(self, client):
        """Test successful quote creation"""
        response = client.post('/api/v1/quotes',
                               json={
                                   'from_currency': 'USD',
                                   'to_currency': 'KES',
                                   'amount': '100.00'
                               }
                               )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'quote_id' in data['data']
        assert data['data']['from_currency'] == 'USD'
        assert data['data']['to_currency'] == 'KES'

    def test_create_quote_missing_fields(self, client):
        """Test quote creation with missing fields"""
        response = client.post('/api/v1/quotes',
                               json={
                                   'from_currency': 'USD'
                               }
                               )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_create_quote_invalid_currency(self, client):
        """Test quote creation with invalid currency"""
        response = client.post('/api/v1/quotes',
                               json={
                                   'from_currency': 'USD',
                                   'to_currency': 'XXX',
                                   'amount': '100.00'
                               }
                               )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_get_quote(self, client):
        """Test retrieving a quote"""
        # Create quote
        create_response = client.post('/api/v1/quotes',
                                      json={
                                          'from_currency': 'USD',
                                          'to_currency': 'EUR',
                                          'amount': '50.00'
                                      }
                                      )
        quote_id = json.loads(create_response.data)['data']['quote_id']

        # Get quote
        response = client.get(f'/api/v1/quotes/{quote_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['quote_id'] == quote_id

    def test_execute_transaction_success(self, client):
        """Test successful transaction execution"""
        # Create quote
        create_response = client.post('/api/v1/quotes',
                                      json={
                                          'from_currency': 'EUR',
                                          'to_currency': 'NGN',
                                          'amount': '200.00'
                                      }
                                      )
        quote_id = json.loads(create_response.data)['data']['quote_id']

        # Execute transaction
        response = client.post('/api/v1/transactions',
                               json={'quote_id': quote_id}
                               )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'transaction_id' in data['data']
        assert data['data']['status'] == 'completed'

    def test_execute_transaction_invalid_quote(self, client):
        """Test transaction execution with invalid quote"""
        response = client.post('/api/v1/transactions',
                               json={'quote_id': 'invalid-id'}
                               )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_get_transaction(self, client):
        """Test retrieving a transaction"""
        # Create and execute
        create_response = client.post('/api/v1/quotes',
                                      json={
                                          'from_currency': 'USD',
                                          'to_currency': 'KES',
                                          'amount': '100.00'
                                      }
                                      )
        quote_id = json.loads(create_response.data)['data']['quote_id']

        execute_response = client.post('/api/v1/transactions',
                                       json={'quote_id': quote_id}
                                       )
        transaction_id = json.loads(execute_response.data)['data']['transaction_id']

        # Get transaction
        response = client.get(f'/api/v1/transactions/{transaction_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['transaction_id'] == transaction_id

    def test_get_all_rates(self, client):
        """Test getting all rates"""
        response = client.get('/api/v1/rates')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) > 0

    def test_set_rate(self, client):
        """Test setting exchange rate"""
        response = client.post('/api/v1/rates',
                               json={
                                   'base_currency': 'USD',
                                   'target_currency': 'EUR',
                                   'rate': '0.93'
                               }
                               )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['rate'] == '0.93'

    def test_get_transaction_history(self, client):
        """Test getting transaction history"""
        # Create and execute a transaction
        create_response = client.post('/api/v1/quotes',
                                      json={
                                          'from_currency': 'USD',
                                          'to_currency': 'KES',
                                          'amount': '100.00'
                                      }
                                      )
        quote_id = json.loads(create_response.data)['data']['quote_id']
        client.post('/api/v1/transactions', json={'quote_id': quote_id})

        # Get history
        response = client.get('/api/v1/transactions')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['count'] > 0