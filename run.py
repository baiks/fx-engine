import os
from app import create_app
from app.services.rate_service import RateService
from flasgger import Swagger

# Get environment or default to development
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

# Initialize Swagger from YAML file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # path: fx-engine/app
SWAGGER_YAML = os.path.join(BASE_DIR, "swagger.yml")   # correct: app/swagger.yml

swagger = Swagger(app, template_file=SWAGGER_YAML)

@app.cli.command()
def seed_rates():
    """Seed initial exchange rates"""
    with app.app_context():
        RateService.seed_initial_rates()
        print("✓ Initial rates seeded successfully")

@app.cli.command()
def update_rates():
    """Update rates from external API"""
    with app.app_context():
        result = RateService.update_rates_from_api()
        print(f"✓ Updated {result['rates_updated']} rates")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)