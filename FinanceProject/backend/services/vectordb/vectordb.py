from database.vectordb_client import chroma_client 
from backend.services.openai.openai_client import openai_client

from typing import List
from datetime import datetime
from pydantic import BaseModel


def search_db(collection, query_texts, n_results, include= ["metadatas","documents"]):
    collection = chroma_client.create_collection(name=collection)
    
    return collection.query(
        query_texts=query_texts, # Chroma will embed this for you
        n_results=n_results, # how many results to return
        include=["metadatas","documents"]   
    )



def vector_db_search_query_agent(query, stock_name):
    """
    Kullanıcının sorusuna göre vektör veritabanında arama yapacak sorguyu üreten ajan.
    """

    todays_date = datetime.now().strftime('%-d %B %Y')

    class SearchQueryModel(BaseModel):
        search_query: List[str]  # Vektör DB'e embedding ile aranacak metin

    prompt = f"""
    Sen bir finansal analiz asistanısın. Görevin, kullanıcının sorusuna göre şirketlerin finansal belgelerinde (KAP, SEC dokümanları, faaliyet raporları gibi) yer alabilecek bir arama cümlesi üretmek.

    Arama, embedding tabanlı vektör veritabanında yapılacaktır. Bu yüzden kısa ama odaklı olmalıdır. 
    Bana, 10 tane query verebilirsin liste içinde. 

    Bugünün tarihi: {todays_date}
    Şirket adı: {stock_name}

    Örnekler:

    Soru: SASA bu sene temettü dağıttı mı?
    Arama: "SASA 2025 temettü kararı"

    Soru: THYAO’nun ortaklık yapısı nedir?
    Arama: "THYAO ortaklık yapısı pay oranları"

    Soru: ASELS 2024 ilk çeyrek finansal raporu açıklandı mı?
    Arama: "ASELS 2024 Q1 finansal sonuçlar"

    Soru: KCHOL son genel kurulda hangi kararları aldı?
    Arama: "KCHOL genel kurul kararları 2025"

    Soru: ENJSA yeni ortak aldı mı?
    Arama: "ENJSA pay devirleri yeni ortak 2025"

    Soru: TUPRS zarar açıkladı mı?
    Arama: "TUPRS dönem net karı 2025"

    Soru: {query}
    Arama:
    """

    

    response = openai_client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0,
        response_format=SearchQueryModel
    )

    return response.choices[0].message.parsed.search_query
