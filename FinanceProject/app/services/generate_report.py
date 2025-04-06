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

    haber_agent_output = haber_agent(query=query, symbol=symbol)

    stock_agent_output = stock_agent(query=query, symbol=symbol)

    final_prompt += haber_agent_output 
    final_prompt += stock_agent_output 



    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": final_prompt}],
        max_tokens=500
    )
