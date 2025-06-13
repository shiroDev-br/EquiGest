from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from fastapi_pagination import add_pagination


from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from equigest.settings import Settings

settings = Settings()
REDIS_URL = settings.REDIS_URL

limiter = Limiter(key_func=get_remote_address, storage_uri=REDIS_URL)

def setup_app():
    app = FastAPI(
        title='EquiGest',
        description='A mare management service',
        version='0.1.0'
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "https://equigest.up.railway.app/", "https://equigest-staging.up.railway.app/"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    add_pagination(app)

    app.state.limiter = limiter
    app.add_exception_handler(429, _rate_limit_exceeded_handler)

    from equigest.routers.auth import auth_router
    from equigest.routers.mare import mare_router
    from equigest.routers.payment import payment_router
    app.include_router(auth_router, tags=['auth'])
    app.include_router(mare_router, tags=['mare'])
    app.include_router(payment_router, tags=['payments'])

    return app