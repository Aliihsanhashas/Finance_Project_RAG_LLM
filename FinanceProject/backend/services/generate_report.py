from backend.services.news.news import haber_agent
from backend.services.stock.stock import stock_agent
from backend.services.openai.openai_client import openai_client



COMMAND_PROMPT = """
Aşağıdaki bilgilere dayanarak, kullanıcıya **doğru, veriye dayalı ve açıklayıcı bir yanıt** üret:

- Cevabın **özlü** ama **tüm önemli detayları kapsayıcı** olmalı.
- Format **MARKDOWN** olmalı.
- Uygunsa **emoji** kullan.
- Kullandığın tüm verileri **kaynak göstererek** kullan.
- Citation formatı şu şekilde olmalı (metin içinde köşeli parantezle, sonunda numaralı listeyle):
  - Metin içinde: [1], [2], ...
  - En altta kaynak listesi:  
    1. Kaynak A  
    2. Kaynak B  
    ...

Kullanıcıdan aldığın bilgiler **soru** ve **bağlam verisi** olarak aşağıda verilecektir. Bu bilgiler doğrultusunda yanıt ver:


**SORU**:     {query}

"""

# query, kullanıcının sorusu

def generate_report(query, symbol):

    final_prompt = COMMAND_PROMPT.format(query=query)
    prompt_compatible_news_data, raw_news_data = haber_agent(query=query, stock_name=symbol)
    raw_stock_data, prompt_compatible_stock_data = stock_agent(query=query, symbol=symbol)

    if prompt_compatible_news_data is not None:
        final_prompt += prompt_compatible_news_data
    else:
        final_prompt += "İlgili haber bilgisi alınamadı.\n"
    
    if prompt_compatible_stock_data is not None:
        final_prompt += prompt_compatible_stock_data
    else:
        final_prompt += "İlgili hisse senedi verisi bulunamadı.\n"



    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": final_prompt}],
        # max_tokens
    )
    ai_response = response.dict()["choices"][0]["message"]["content"]

    return {"ai_response": ai_response, "stock_data":raw_stock_data , "haber_data":raw_news_data, "vector_data": None}
