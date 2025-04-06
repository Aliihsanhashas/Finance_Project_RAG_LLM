from isyatirimhisse import StockData
from app.services.openai.openai_client import openai_client
from datetime import datetime
from pydantic import BaseModel

def stock_data_prompt_builder(data_dict):
    result = []
    stock_code = data_dict.get("CODE", {}).get(0, "Unknown")
    result.append(f"Stock Data for {stock_code}:")
    
    for idx in range(len(data_dict["DATE"])):
        date_str = data_dict["DATE"].get(idx, "Unknown")
        closing_tl = data_dict["CLOSING_TL"].get(idx, "N/A")
        low_tl = data_dict["LOW_TL"].get(idx, "N/A")
        high_tl = data_dict["HIGH_TL"].get(idx, "N/A")
        volume_tl = data_dict["VOLUME_TL"].get(idx, "N/A")
        closing_usd = data_dict["CLOSING_TL"].get(idx, "N/A")
        low_usd = data_dict["LOW_TL"].get(idx, "N/A")
        high_usd = data_dict["HIGH_TL"].get(idx, "N/A")
        volume_usd = data_dict["VOLUME_TL"].get(idx, "N/A")
        xu100_tl = data_dict["XU100_TL"].get(idx, "N/A")
        xu100_usd = data_dict["XU100_TL"].get(idx, "N/A")
        
        result.append(
            f"Date: {date_str}\n"
            f"  - Closing Price: {closing_tl} TL ({closing_usd} USD)\n"
            f"  - Low: {low_tl} TL ({low_usd} USD)\n"
            f"  - High: {high_tl} TL ({high_usd} USD)\n"
            f"  - Volume: {volume_tl} TL ({volume_usd} USD)\n"
            f"  - XU100 Index: {xu100_tl} TL ({xu100_usd} USD)\n"
        )
    return "\n".join(result)

def get_stock_data(symbols, start_date, end_date=None, exchange="0", frequency="1d", observation="last", return_type="0"):
    """
    exchange : The options are '0' for TL columns, '1' for USD columns, or '2' for both TL and USD columns.")
    symbols : "THYAO" or ["THYAO", "KCHOL"]
    start_date : "dd-mm-yyyy" , '18-03-2025'
    end_date : 'The options are '1d', '1w', '1mo', '3mo', or '1y'."
    frequency : "dd-mm-yyyy" , '18-03-2025'
    observation : observation (str, varsayılan 'last'): Haftalık, aylık ve yıllık frekanslarda istenen gözlem ('last': Son, 'mean': Ortalama).
    return_type : return_type (str, varsayılan '0'): Ham veriler mi kullanılacak yoksa getiri mi hesaplanacak? ('0': Ham, '1': Logaritmik Getiri, '2': Basit Getiri)


    """
    stock_data = StockData().get_data(symbols, start_date, end_date, exchange, frequency, observation, return_type)
    return stock_data_prompt_builder(stock_data.to_dict())


def stock_query_generator(query, stock_name):
    """
    Kullanıcının sorusuna göre get_stock_data fonksiyonuna uygun parametreleri belirleyen ajan.
    """

    todays_date = datetime.now().strftime('%-d %B %Y')
      
    class StockAPIDataModel(BaseModel):
        start_date: str
        end_date: str
        exchange: str
        frequency: str
        observation: str
        return_type: str

    prompt = f"""
    Sen bir finansal veri analistisin. Aşağıdaki kullanıcı sorusuna göre bir hisse senedi verisi API'sine çağrı yapacaksın.
    Bugünün tarihi : {todays_date} 
    Hisse senedi: {stock_name}
    Soru: {query}
    
    API fonksiyonunun aldığı parametreler:
    - start_date : "dd-mm-yyyy" biçiminde başlangıç tarihi
    - end_date : (opsiyonel) "dd-mm-yyyy" biçiminde bitiş tarihi
    - exchange : '0' → TL, '1' → USD, '2' → TL ve USD
    - frequency : '1d', '1w', '1mo', '3mo', '1y' (veri sıklığı)
    - observation : 'last', 'mean' gibi gözlem tipi
    - return_type : '0' → Ham veri, '1' → Logaritmik Getiri, '2' → Basit Getiri

    Görev:
    Kullanıcı sorusuna göre bu parametrelerin değerlerini belirle.

    Örnekler:

    Soru: Son hafta THY'e ne oldu?
    Cevap:
    {{
      "start_date": "5-03-2025",
      "end_date": "12-03-2025",
      "exchange": "0",
      "frequency": "1d",
      "observation": "last",
      "return_type": "0"
    }}

    Soru: Son 3 ayda dolar bazında SASA getirisi nasıldı?
    Cevap:
    {{
      "start_date": "12-12-2024",
      "end_date": "12-03-2025",
      "exchange": "1",
      "frequency": "1m",
      "observation": "last",
      "return_type": "1"
    }}


    Soru: Son 1 senede aylık TL bazında KUKU getirisi nasıldı?
    Cevap:
    {{
      "start_date": "12-12-2024",
      "end_date": "12-03-2025",
      "exchange": "0",
      "frequency": "1m",
      "observation": "last",
      "return_type": "1"
    }}

    Soru: {query}
    Cevap:
    """

    response = openai_client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0,
        response_format=StockAPIDataModel,

    )

    return response.choices[0].message.parsed



def stock_agent(query, symbol):

    query_params = stock_query_generator(query, symbol)

    stock_data_llm_query = stock_data_api_agent_output.dict() 
    return get_stock_data(symbols=symbol,  **stock_data_llm_query )