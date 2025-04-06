from fastapi import APIRouter, Depends, HTTPException

from app.services.generate_report import generate_report
# from app.schemas.auth.LoginSchema import LoginSchema


agent_router = APIRouter(
    tags=["Rapor"],
    prefix='/rapor'
    )


@agent_router.post("/generate-report", response_model=dict)
async def loginUser(query : str, symbol:str = "THYAO"):    
    return generate_report(query=query, symbol=symbol)
