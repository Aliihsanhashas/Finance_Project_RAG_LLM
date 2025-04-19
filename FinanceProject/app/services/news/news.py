import requests

from app.services.openai.openai_client import openai_client


BASE_URL = "https://newsapi.org/v2/everything"
API_KEY = "6e3b3a8dde1340878504f8cd492df0d8"

def get_news(q: str = "SASA"):
    params = {
        "q": q,  
        "language": "tr",  # Türkçe haberler için
        "apiKey": "6e3b3a8dde1340878504f8cd492df0d8"
    }
    
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        raw_news_data = response.json()
        return haber_data_prompt_builder(raw_news_data), raw_news_data["articles"]
    else:
        return "Son haberlere ulaşamıyorum", []


def haber_data_prompt_builder(haber_data):
    prompt = ""

    if haber_data["totalResults"] == 0: 
        prompt += "Son haberlere ulaşamıyorum\n"


    for idx, haber in enumerate(haber_data["articles"]):
        prompt += f"{idx}. Haber : \n"
        prompt += f"Başlık : {haber['title']}\n"
        prompt += f"Tarih : {haber['publishedAt']}\n"
        prompt += f"Yazar : {haber['author']}\n"
        prompt += f"Özet : {haber['description']}\n"
        prompt += f"İçerik : {haber['content']}\n"
        prompt += f"--"*10 + "\n"
    return prompt


def haber_query_generator(query, stock_name):
    """
    Kullanıcının sorusuna göre hangi haberin alınması gerektiğini araştıran ajan.
    """

    prompt = f"""
    Sen bir finans analistisin. {stock_name} ile ilgili internetten araştırma yapıyorsun. Kullanıcının sorusuna ve verilen hisseye göre, internete hangi aramayı yapman gerektiğini bulmalısın.
    
    Araştıracağın stok adı : {stock_name} 

    Örnekler: 
    Soru : THYAO'nın hisse değeri bu yaz artacak mı? Turizm 2024 yılında nasıl devam ediyor.
    Cevap : 2024 Turizm Türkiye 

    Soru : Polyester satışları dünyada nasıl gidiyor, SASA etkilenir mi? 
    Cevap : Polyester sales 2024

    Soru : {query}
    Cevap : 
    """


    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )

    return response.choices[0].message.content


def haber_agent(query, stock_name): 
    # haber_queries = haber_query_generator(stock_name, stock_name)
    prompt_compatible_news_data, raw_news_data = get_news(stock_name)
    return prompt_compatible_news_data, raw_news_data 