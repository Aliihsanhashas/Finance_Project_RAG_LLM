from fastapi import APIRouter

from app.api.controllers.agents import agent_router as agent_api

router = APIRouter()


def includeApiRoutes():
    ''' Include to router all api rest routes with version prefix '''
    router.include_router(agent_api)
    # iş bankasında hissenin günlük/aylık/yıllık isteğe göre verisini veren api.




includeApiRoutes()