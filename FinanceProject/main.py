from fastapi import Depends, FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.middlewares.loggerMiddleware import LoggerMiddleware

from app.routes.api import router

# from settings import settings

def InitApplication() -> FastAPI:

    ## Create FastApi App
    fastApiApp = FastAPI()

    ## Mapping api routes
    fastApiApp.include_router(router)

    ## Custom Middlewares
    # fastApiApp.add_middleware(LoggerMiddleware)

    ## Allow cors
    """
    fastApiApp.add_middleware( CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    """

    return fastApiApp


app = InitApplication()