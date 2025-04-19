from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.generate_report import generate_report

agent_router = APIRouter(
    tags=["Rapor"],
    prefix='/rapor'
)

class RaporCevabi(BaseModel):
    rapor: str

@agent_router.post("/generate-report" ) # response_model=RaporCevabi
async def loginUser(query : str, symbol: str = "THYAO"):
    return generate_report(query=query, symbol=symbol)