try:
    from mangum import Mangum
    from app.main import app
    handler = Mangum(app, lifespan="off")
except ImportError:
    # Mangum is only required in AWS Lambda execution environment
    handler = None
