from fastapi import FastAPI

def setup_app():
    app = FastAPI(
        title='EquiGest',
        description='A mare management service',
        version='0.1.0'
    )

    return app