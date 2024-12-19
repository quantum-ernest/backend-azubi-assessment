"""
FastAPI application setup for a Product List and Shopping Cart API.

This application includes various routes for managing users, products, shopping cart, and roles, and it sets up middleware for rate limiting and CORS handling. The application also initializes the database with default data on startup.

Key Components:
- **Lifespan Context**: The `lifespan` context manager runs on app startup, setting default data in the database.
- **Rate Limiting**: Configured using `slowapi`, limiting requests to 50 per minute from a single IP address.
- **CORS Middleware**: Allows cross-origin requests from any origin, supporting credentials and any methods or headers.
- **SlowAPI Middleware**: Implements rate limiting to protect the API from excessive usage.
- **Database Models**: `Base.metadata.create_all(bind=engine)` ensures the database tables are created on startup.

Included Routers:
- `auth_router`: Authentication-related routes.
- `user_router`: Routes for managing users.
- `product_router`: Routes for managing products.
- `cart_router`: Routes for managing the shopping cart.
- `role_router`: Routes for managing user roles.

Exception Handling:
- Handles rate limit exceed errors with a custom handler.

Main Route:
- A root endpoint (`/`) returns a basic API information message.

Configuration:
- The app is configured to support CORS from all origins and includes rate limiting using SlowAPI.
"""

from fastapi import FastAPI
from starlette.responses import RedirectResponse

from controllers import (
    auth_router,
    role_router,
    cart_router,
    user_router,
    product_router,
)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from contextlib import asynccontextmanager
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware

from core import set_default_data, engine
from models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    set_default_data()
    yield


Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address, default_limits=["50/minutes"])

app = FastAPI(
    title="API FOR PRODUCT LIST AND SHOPPING CART - ASSESSMENT",
    description="‼️‼️‼️‼️**ADMIN DEFAULT PASSWORD IS PROVIDED IN THE DESCRIPTION OF THE LOGIN ENDPOINT** '/auth/login' ‼️‼️‼️‼️",
    lifespan=lifespan,
)


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SlowAPIMiddleware)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(product_router)
app.include_router(cart_router)
app.include_router(role_router)


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")
