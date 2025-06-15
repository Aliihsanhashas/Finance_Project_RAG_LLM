from isyatirimhisse import StockData
from backend.services.openai.openai_client import openai_client
from datetime import datetime
from pydantic import BaseModel

def stock_data_prompt_builder(data_dict):
    result = []
    stock_code = data_dict.get("CODE", {}).get(0, "Unknown")
    result.append(f"Stock Data for {stock_code}:")
    
    # Mevcut kolonları kontrol et
    has_usd_columns = any("USD" in str(key) for key in data_dict.keys())
    has_tl_columns = any("TL" in str(key) for key in data_dict.keys())
    
    for idx in range(len(data_dict["DATE"])):
        date_str = data_dict["DATE"].get(idx, "Unknown")
        
        # TL değerleri
        closing_tl = data_dict.get("CLOSING_TL", {}).get(idx, "N/A")
        low_tl = data_dict.get("LOW_TL", {}).get(idx, "N/A")
        high_tl = data_dict.get("HIGH_TL", {}).get(idx, "N/A")
        volume_tl = data_dict.get("VOLUME_TL", {}).get(idx, "N/A")
        xu100_tl = data_dict.get("XU100_TL", {}).get(idx, "N/A")
        
        # USD değerleri (eğer mevcutsa)
        if has_usd_columns:
            closing_usd = data_dict.get("CLOSING_USD", {}).get(idx, "N/A")
            low_usd = data_dict.get("LOW_USD", {}).get(idx, "N/A")
            high_usd = data_dict.get("HIGH_USD", {}).get(idx, "N/A")
            volume_usd = data_dict.get("VOLUME_USD", {}).get(idx, "N/A")
            xu100_usd = data_dict.get("XU100_USD", {}).get(idx, "N/A")
        else:
            closing_usd = low_usd = high_usd = volume_usd = xu100_usd = "N/A"
        
        # Çıktı formatı
        if has_tl_columns and has_usd_columns:
            result.append(
                f"Date: {date_str}\n"
                f"  - Closing Price: {closing_tl} TL ({closing_usd} USD)\n"
                f"  - Low: {low_tl} TL ({low_usd} USD)\n"
                f"  - High: {high_tl} TL ({high_usd} USD)\n"
                f"  - Volume: {volume_tl} TL ({volume_usd} USD)\n"
                f"  - XU100 Index: {xu100_tl} TL ({xu100_usd} USD)\n"
            )
        elif has_tl_columns:
            result.append(
                f"Date: {date_str}\n"
                f"  - Closing Price: {closing_tl} TL\n"
                f"  - Low: {low_tl} TL\n"
                f"  - High: {high_tl} TL\n"
                f"  - Volume: {volume_tl} TL\n"
                f"  - XU100 Index: {xu100_tl} TL\n"
            )
        elif has_usd_columns:
            result.append(
                f"Date: {date_str}\n"
                f"  - Closing Price: {closing_usd} USD\n"
                f"  - Low: {low_usd} USD\n"
                f"  - High: {high_usd} USD\n"
                f"  - Volume: {volume_usd} USD\n"
                f"  - XU100 Index: {xu100_usd} USD\n"
            )
    
    return "\n".join(result)

def get_stock_data(symbols, start_date, end_date=None, exchange="2", frequency="1d", observation="last", return_type="0"):
    """
    exchange : The options are '0' for TL columns, '1' for USD columns, or '2' for both TL and USD columns.
    symbols : "THYAO" or ["THYAO", "KCHOL"]
    start_date : "dd-mm-yyyy" , '18-03-2025'
    end_date : "dd-mm-yyyy" , '18-03-2025'
    frequency : 'The options are '1d' for daily, '1w' : for weekly freq.  , '1mo' : monthly freq, '3mo' : quarterly freq. , or '1y' : for annual freq.  
    observation : observation (str, varsayılan 'last'): Haftalık, aylık ve yıllık frekanslarda istenen gözlem ('last': Son, 'mean': Ortalama).
    return_type : return_type (str, varsayılan '0'): Ham veriler mi kullanılacak yoksa getiri mi hesaplanacak? ('0': Ham, '1': Logaritmik Getiri, '2': Basit Getiri)
    """
    try:
        stock_data = StockData().get_data(symbols, start_date, end_date, exchange, frequency, observation, return_type)
        if stock_data is None or stock_data.empty:
            return "Belirtilen kriterlere uygun hisse senedi verisi bulunamadı.", None
        
        # Debug: Mevcut kolonları yazdır
        print("Mevcut kolonlar:", list(stock_data.columns))
        
        return stock_data_prompt_builder(stock_data.to_dict()), stock_data
    except Exception as e:
        return f"Veri çekme hatası: {str(e)}", None

def stock_query_generator(query, stock_name):
    """
    Kullanıcının sorusuna göre get_stock_data fonksiyonuna uygun parametreleri belirleyen ajan.
    """
    todays_date = datetime.now().strftime('%d-%m-%Y')  # Düzeltildi: %#d yerine %d
      
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
    - exchange : '0' → TL, '1' → USD, '2' → TL ve USD (varsayılan '2')
    - frequency : '1d', '1w', '1mo', '3mo', '1y' (veri sıklığı)
    - observation : 'last', 'mean' gibi gözlem tipi
    - return_type : '0' → Ham veri, '1' → Logaritmik Getiri, '2' → Basit Getiri

    Görev:
    Kullanıcı sorusuna göre bu parametrelerin değerlerini belirle.
    Özellikle dikkat et:
    - Exchange varsayılan olarak '2' olsun (hem TL hem USD için)
    - Tarihleri doğru hesapla

    Örnekler:

    Soru: Son hafta THY'e ne oldu?
    Cevap:
    {{
      "start_date": "08-06-2025",
      "end_date": "15-06-2025",
      "exchange": "2",
      "frequency": "1d",
      "observation": "last",
      "return_type": "0"
    }}

    Soru: Son 3 ayda dolar bazında SASA getirisi nasıldı?
    Cevap:
    {{
      "start_date": "15-03-2025",
      "end_date": "15-06-2025",
      "exchange": "1",
      "frequency": "1mo",
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
    try:
        query_params = stock_query_generator(query, symbol)
        stock_data_llm_query = query_params.dict()
        prompt_compatible_stock_data, raw_stock_data = get_stock_data(symbols=symbol, **stock_data_llm_query)
        
        if raw_stock_data is not None:
            raw_stock_data['DATE'] = raw_stock_data['DATE'].astype(str)
            raw_stock_data = raw_stock_data.T.to_dict()
            
        return raw_stock_data, prompt_compatible_stock_data
    except Exception as e:
        return None, f"Stock agent hatası: {str(e)}"