
import gradio as gr
import requests
import pandas as pd
import plotly.express as px 


def generate_report(symbol, question):
    url = "http://backend:8000/rapor/generate-report"
    params = {"symbol": symbol, "query":question}
    headers = {"accept": "application/json"}
    response = requests.post(url, params=params, headers=headers).json()
   

    ai_response = response.get("ai_response", "")
    stock_data = pd.DataFrame(response.get("stock_data", {}).values())
    haber_data = response.get("haber_data", [])
    news_titles = [haber.get("title", "Unknown") for haber in haber_data]
    news_map = {haber.get("title", "Unknown"): f"🔗 [{haber.get('title')}]({haber.get('url')})\n\n{haber.get('description', '')}" for haber in haber_data}

    return ai_response, stock_data, news_titles, news_map


def update_everything(symbol, question):
    ai_resp, stock_df, titles, news_map = generate_report(symbol, question)

    if stock_df is None or stock_df.empty:
        fig = px.line(title="No Data Found")
    else:
        stock_df['DATE'] = pd.to_datetime(stock_df['DATE'])
        fig = px.line(stock_df, x='DATE', y='CLOSING_TL', title='Stock Price Over Time',
                      labels={'DATE': 'Date', 'CLOSING_TL': 'Closing Price (TL)'})
        fig.update_layout(template="plotly_dark", title_x=0.5)

    news_titles = titles
    first_news = news_map.get(titles[0], "") if titles else ""

    return (
        ai_resp,
        stock_df,
        fig,
        gr.update(choices=news_titles, value=news_titles[0] if news_titles else None),
        first_news,
        news_map
    )




def plot_stock_data(stock_data, price_column='CLOSING_TL', title_suffix=''):
    """
    Geliştirilmiş stock plot fonksiyonu
    
    Args:
        stock_data: Dict veya DataFrame formatında stock verisi
        price_column: Çizilecek fiyat kolonu ('CLOSING_TL', 'CLOSING_USD', etc.)
        title_suffix: Başlığa eklenecek ek metin
    """
    
    # Veri tipini kontrol et ve DataFrame'e çevir
    if isinstance(stock_data, dict):
        # Dictionary ise DataFrame'e çevir
        df = pd.DataFrame.from_dict(stock_data, orient='index')
        print(f"Converted dict to DataFrame. Shape: {df.shape}")
    elif isinstance(stock_data, pd.DataFrame):
        df = stock_data.copy()
        print(f"Already DataFrame. Shape: {df.shape}")
    else:
        raise ValueError(f"Unsupported data type: {type(stock_data)}")
    
    # Debug: DataFrame içeriğini kontrol et
    print("DataFrame columns:", df.columns.tolist())
    print("DataFrame dtypes:")
    print(df.dtypes)
    print("\nFirst few rows:")
    print(df.head())
    
    # Gerekli kolonları kontrol et
    if 'DATE' not in df.columns:
        raise ValueError("DATE column not found in data")
    
    if price_column not in df.columns:
        available_columns = [col for col in df.columns if 'CLOSING' in col or 'HIGH' in col or 'LOW' in col]
        raise ValueError(f"{price_column} column not found. Available price columns: {available_columns}")
    
    # DATE kolonunu datetime'a çevir
    try:
        df['DATE'] = pd.to_datetime(df['DATE'])
    except Exception as e:
        print(f"Error converting DATE: {e}")
        print("DATE column sample values:", df['DATE'].head().tolist())
        # Alternatif çevirme yöntemleri dene
        try:
            df['DATE'] = pd.to_datetime(df['DATE'], format='%Y-%m-%d')
        except:
            try:
                df['DATE'] = pd.to_datetime(df['DATE'], format='%d-%m-%Y')
            except:
                print("Could not convert DATE column. Using as string.")
    
    # Fiyat kolonunu numeric'e çevir
    try:
        df[price_column] = pd.to_numeric(df[price_column], errors='coerce')
    except Exception as e:
        print(f"Error converting {price_column}: {e}")
    
    # NaN değerleri temizle
    df_clean = df.dropna(subset=[price_column])
    
    if df_clean.empty:
        raise ValueError(f"No valid data found for {price_column}")
    
    # Değer aralığını kontrol et
    min_val = df_clean[price_column].min()
    max_val = df_clean[price_column].max()
    print(f"\nPrice range: {min_val:.6f} - {max_val:.6f}")
    
    # Eğer değerler çok küçükse (normalize edilmişse) uyarı ver
    if max_val < 1:
        print("⚠️  WARNING: Values seem very small (possibly normalized). Consider scaling.")
        title_suffix += " (Values may be normalized)"
    
    # Tarihe göre sırala
    df_clean = df_clean.sort_values('DATE')
    
    # Grafik oluştur
    currency = 'TL' if 'TL' in price_column else 'USD' if 'USD' in price_column else 'Units'
    
    fig = px.line(
        df_clean, 
        x='DATE', 
        y=price_column, 
        title=f'Stock Price Over Time {title_suffix}',
        labels={
            'DATE': 'Date', 
            price_column: f'Price ({currency})'
        },
        hover_data=[price_column]
    )
    
    # Layout güncellemeleri
    fig.update_layout(
        template="plotly_dark", 
        title_x=0.5,
        xaxis_title="Date",
        yaxis_title=f"Price ({currency})",
        hovermode='x unified'
    )
    
    # Y ekseni formatını ayarla
    if max_val < 1:
        fig.update_yaxis(tickformat='.6f')  # Çok küçük değerler için daha fazla decimal
    else:
        fig.update_yaxis(tickformat='.2f')
    
    return fig

def update_news_content(selected_title, news_map):
    return news_map.get(selected_title, "")

def update_news_display(symbol, question):
    ai_resp, stock_df, titles, news_map = generate_report(symbol, question)
    return ai_resp, stock_df, gr.update(choices=titles, value=titles[0] if titles else None), news_map.get(titles[0], ""), news_map, stock_df

with gr.Blocks() as demo:
    gr.Markdown("# 📊 Financial RAG Assistant")

    with gr.Row():
        symbol_input = gr.Textbox(label="Ticker Symbol (e.g., THYAO)", value="THYAO")
        question_input = gr.Textbox(label="Ask a question", placeholder="How is THYAO doing?")
        submit_btn = gr.Button("Research")

    with gr.Row():
        with gr.Column(scale=1):
            with gr.Tabs():
                with gr.TabItem("📊 Stock Plot"):
                    stock_plot = gr.Plot(label="Stock Price Plot")
                with gr.TabItem("📰 News"):
                    news_dropdown = gr.Dropdown(label="Select a News Headline", choices=[], value=None)
                    selected_news_output = gr.Markdown()

        with gr.Column(scale=1):
            ai_output = gr.Markdown(label="🧠 AI Analysis")

    news_state = gr.State()
    stock_data_state = gr.State()

    submit_btn.click(
        update_everything,
        inputs=[symbol_input, question_input],
        outputs=[ai_output, stock_data_state, stock_plot, news_dropdown, selected_news_output, news_state]
    )

    news_dropdown.change(
        update_news_content,
        inputs=[news_dropdown, news_state],
        outputs=[selected_news_output]
    )





if __name__ == "__main__":
    demo.launch()


