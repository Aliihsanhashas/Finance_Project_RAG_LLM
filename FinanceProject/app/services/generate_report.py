from app.services.news.news import haber_agent
from app.services.stock.stock import stock_agent
from app.services.openai.openai_client import openai_client



COMMAND_PROMPT = """
    Bu bilgilere dayanarak, kullanıcıya doğru ve detaylı bir yanıt ver. Özetleyerek ancak tüm önemli detayları kapsayarak açıklayıcı bir cevap üret.

    Cevabın MARKDOWN FORMATINDA OLMALI. Veriye dayanmalı. Kullandığın tüm verileri cite et. Emoji kullan.
    
    Aşağıda sana verilecek bilgiler ışığında, bu soruyu cevaplar mısın?

    {query}

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
