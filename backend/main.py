from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter
from app.core.config import settings
from app.api.endpoints import products, auth, smart_cart

# Initialize the FastAPI application
app = FastAPI(
    title = settings.PROJECT_NAME,
    version = settings.PROJECT_VERSION,
    description = settings.PROJECT_DESCRIPTION
)

# Add the rate limiter to the application
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include the authentication router
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

# Include the products router
app.include_router(products.router, prefix="/api/v1", tags=["products"])

# Include the smart cart router
app.include_router(smart_cart.router, prefix="/api/v1/smart-cart", tags=["smart_cart"])

@app.get("/")
def read_root():
    """
    Root endpoint to check if the API is running.
    """
    return {"message": "Welcome to the Smart Cart API!"}