###  günlük aylık ya da yıllık, verilen hisse adına göre veri veren endpoint
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.stock.stock import stock_agent

stock_router = APIRouter(
    prefix="/stocks", 
    tags=["Hisse Senedi"]
    )

class RaporCevabi(BaseModel):
    rapor: str

@stock_router.get("/stock-agent", response_model=RaporCevabi)
async def loginUser(query : str, symbol: str):
    rapor_icerigi = stock_agent(query=query, symbol=symbol)
    return {"rapor": rapor_icerigi}




