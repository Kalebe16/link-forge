import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from link_forge.auth.api import router as auth_router
from link_forge.health.api import router as health_router
from link_forge.links.api import router as links_router
from link_forge.redirect.api import router as redirect_router


def create_app() -> FastAPI:
    app = FastAPI(title='LinkForge')
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=os.environ['CORS_ORIGINS'].split(','),
        allow_methods=['*'],
        allow_headers=['*'],
    )
    app.include_router(auth_router)
    app.include_router(links_router)
    app.include_router(health_router)
    app.include_router(redirect_router)
    return app


def main() -> None:
    app = create_app()
    uvicorn.run(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    main()
