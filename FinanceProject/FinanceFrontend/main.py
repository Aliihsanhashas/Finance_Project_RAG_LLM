
import gradio as gr
import requests
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go


def generate_report(symbol, question):
    url = "http://backend:8000/rapor/generate-report"
    params = {"symbol": symbol, "query": question}
    headers = {"accept": "application/json"}
    response = requests.post(url, params=params, headers=headers).json()

    ai_response = response.get("ai_response", "")
    stock_data = pd.DataFrame(response.get("stock_data", {}).values())

    # Existing news extraction:
    haber_data = response.get("haber_data", [])
    news_titles = [haber.get("title", "Unknown") for haber in haber_data]
    news_map = {
        haber.get("title", "Unknown"): f"🔗 [{haber.get('title')}]({haber.get('url')})\n\n{haber.get('description', '')}"
        for haber in haber_data
    }

    # New vector data extraction, repeating same pattern for vectordb_results:
    vectordb_results = response.get("vector_data", [])
    vector_titles = [item.get("file_name", "Unknown") for item in vectordb_results]
    vector_map = {
        item.get("file_name", "Unknown"): item.get("content", "")
        for item in vectordb_results
    }

    return ai_response, stock_data, news_titles, news_map, vector_titles, vector_map

def update_everything(symbol, question):
    ai_resp, stock_df, news_titles, news_map, vector_titles, vector_map = generate_report(symbol, question)
    
    stock_df = stock_df.dropna(subset=['DATE', 'CLOSING_TL'])

    if stock_df is None or stock_df.empty:
        fig = px.line(title="No Data Found")
    else:
        stock_df['DATE'] = pd.to_datetime(stock_df['DATE'])
        stock_df['CLOSING_TL'] = pd.to_numeric(stock_df['CLOSING_TL'], errors='coerce')
        stock_df['CLOSING_TL'] = stock_df['CLOSING_TL'].fillna(method='bfill')
        fig = go.Figure([
            go.Scatter(
                x=stock_df['DATE'],
                y=stock_df['CLOSING_TL'],
                mode='lines+markers',
                name='Closing Price'
            )
        ])
        fig.update_layout(title='Stock Price Over Time', xaxis_title='Date', yaxis_title='Closing TL')

    first_news = news_map.get(news_titles[0], "") if news_titles else ""
    first_vector = vector_map.get(vector_titles[0], "") if vector_titles else ""

    return (
        ai_resp,
        stock_df,
        fig,
        gr.update(choices=news_titles, value=news_titles[0] if news_titles else None),
        first_news,
        news_map,
        gr.update(choices=vector_titles, value=vector_titles[0] if vector_titles else None),
        first_vector,
        vector_map
    )

def update_news_content(selected_title, news_map):
    return news_map.get(selected_title, "")

def update_vector_content(selected_file_name, vector_map):
    return vector_map.get(selected_file_name, "")

# In your Gradio UI definition, add vector dropdown and markdown in the same way as news:

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
                with gr.TabItem("📂 Vector DB Results"):
                    vector_dropdown = gr.Dropdown(label="Select a File Name", choices=[], value=None)
                    selected_vector_output = gr.Markdown()

        with gr.Column(scale=1):
            ai_output = gr.Markdown(label="🧠 AI Analysis")

    news_state = gr.State()
    stock_data_state = gr.State()
    vector_state = gr.State()  # new state for vector map

    submit_btn.click(
        update_everything,
        inputs=[symbol_input, question_input],
        outputs=[
            ai_output,
            stock_data_state,
            stock_plot,
            news_dropdown,
            selected_news_output,
            news_state,
            vector_dropdown,
            selected_vector_output,
            vector_state
        ]
    )

    news_dropdown.change(
        update_news_content,
        inputs=[news_dropdown, news_state],
        outputs=[selected_news_output]
    )

    vector_dropdown.change(
        update_vector_content,
        inputs=[vector_dropdown, vector_state],
        outputs=[selected_vector_output]
    )


if __name__ == "__main__":
    demo.launch()
