from fastapi import FastAPI

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

def setup_app():
    app = FastAPI(
        title='EquiGest',
        description='A mare management service',
        version='0.1.0'
    )

    app.state.limiter = limiter
    app.add_exception_handler(429, _rate_limit_exceeded_handler)

    from equigest.routers.auth import auth_router
    from equigest.routers.mare import mare_router
    app.include_router(auth_router, tags=['auth'])
    app.include_router(mare_router, tags=['mare'])

    return app