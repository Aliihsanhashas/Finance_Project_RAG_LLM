from app.services.news.news import haber_agent
from app.services.stock.stock import stock_agent
from app.services.openai.openai_client import openai_client



COMMAND_PROMPT = """
    Bu bilgilere dayanarak, kullanıcıya doğru ve detaylı bir yanıt ver. Özetleyerek ancak tüm önemli detayları kapsayarak açıklayıcı bir cevap üret.

    RAPOR MARKDOWN FORMATINDA OLMALI.
    5 SECTION İÇERMELİ. GİRİŞ GELİŞME ANALİZ TAHMIN SONUÇ

"""

# query, kullanıcının sorusu

def generate_report(query, symbol):

    final_prompt = """ {COMMAND_PROMPT} """

    haber_agent_output = haber_agent(query=query, stock_name=symbol)
    stock_agent_output = stock_agent(query=query, symbol=symbol)

    if haber_agent_output is not None:
        final_prompt += haber_agent_output
    else:
        final_prompt += "İlgili haber bilgisi alınamadı.\n"

    if stock_agent_output is not None:
        final_prompt += stock_agent_output
    else:
        final_prompt += "İlgili hisse senedi verisi bulunamadı.\n"

    return final_prompt


    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": final_prompt}],
        max_tokens=500
    )
