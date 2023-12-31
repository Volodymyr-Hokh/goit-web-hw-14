"""
This is the main file of the application.
It sets up the FastAPI application, adds middleware, and includes routers for different endpoints.

The routers included are:
- contacts.router: Handles API endpoints related to contacts.
- auth.router: Handles API endpoints related to authentication.
- users.router: Handles API endpoints related to users.

The application also handles rate limiting using the limiter defined in src.limiter module.

The CORS middleware is added to allow requests from the specified origin.

Note: This file should be run to start the application.
"""

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware

from src.limiter import limiter
from src.routes import auth, contacts, users


app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = ["http://localhost:3000"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
