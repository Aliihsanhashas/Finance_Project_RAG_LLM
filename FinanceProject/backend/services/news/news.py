import requests

from backend.services.openai.openai_client import openai_client


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
You are a financial analyst. You are researching information on the internet about {stock_name}. Based on the user's question and the given stock, you need to determine what search query you should use on the internet.

Stock to research: {stock_name}

Examples:

Question: Will THYAO's stock price rise this summer? How is tourism in 2024?
Answer: 2024 tourism Turkey

Question: How has THYAO's stock performed in recent months? Has the Israel-Iran conflict affected it?
Answer: Israel Iran flight suspensions

Question: How are global polyester sales going? Could this affect SASA?
Answer: Polyester sales 2024

Question: When will ASELS receive new defense contracts? Are defense expenditures increasing?
Answer: Turkey defense spending 2024 contracts

Question: Is BİM’s profit affected by inflation? How is consumer confidence?
Answer: Turkey consumer confidence 2024 inflation impact

Question: Will Pegasus’ profits rise? Are jet fuel prices going down?
Answer: Jet fuel prices 2024 trend

Question: Is TUPRS affected by Iran sanctions?
Answer: Iran oil sanctions 2024 Turkey impact

Question: Why is HEKTS stock declining? How is the agriculture sector doing?
Answer: Turkey agriculture sector 2024 outlook

Question: How are Migros’ online sales doing?
Answer: Migros online sales growth 2024

Question: What are Kardemir’s production targets? What is the demand for steel like?
Answer: Global steel demand 2024 Kardemir plans

Question: Is Arçelik expanding abroad? How are white goods sales in Europe?
Answer: Europe white goods sales 2024 Arçelik expansion

Question: Will Türk Telekom’s revenue grow? Where is 5G investment heading?
Answer: Turkey 5G investment 2024 telecom growth

Question: Is the company growing through exports? Is it affected by the USD/TRY exchange rate?
Answer: USD to TRY 2024 impact on Turkish exports

Question: {query}
Answer:

    """


    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )

    return response.choices[0].message.content


def haber_agent(query, stock_name): 
    # haber_queries = haber_query_generator(stock_name, stock_name)
    prompt_compatible_news_data, raw_news_data = get_news(stock_name)
    return prompt_compatible_news_data, raw_news_data 