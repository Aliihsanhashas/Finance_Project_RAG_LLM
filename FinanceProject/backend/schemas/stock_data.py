from pydantic import BaseClass 

    
class StockAPIDataModel(BaseClass):
    start_date: str
    end_date: str
    exchange: str
    frequency: str
    observation: str
    return_type: str
