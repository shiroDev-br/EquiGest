from fastapi import FastAPI

def setup_app():
    app = FastAPI(
        title='EquiGest',
        description='A mare management service',
        version='0.1.0'
    )

    from equigest.routers.auth import auth_router
    app.include_router(auth_router, tags=['auth'])

    return app