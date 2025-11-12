import pytest
from app import create_app, db
from app.services.rate_service import RateService


@pytest.fixture
def app():
    """Create and configure a test app"""
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        # Seed test data
        RateService.seed_initial_rates()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for making requests"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner for testing commands"""
    return app.test_cli_runner()