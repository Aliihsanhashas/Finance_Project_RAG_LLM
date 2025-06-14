from fastapi import APIRouter

from backend.api.controllers.agents import agent_router as agent_api
from backend.api.controllers.stock import stock_router as stock_api

router = APIRouter()


def includeApiRoutes():
    ''' Include to router all api rest routes with version prefix '''
    router.include_router(agent_api)
    # iş bankasında hissenin günlük/aylık/yıllık isteğe göre verisini veren api.
    router.include_router(stock_api)




includeApiRoutes()
__all__ = ["router"]