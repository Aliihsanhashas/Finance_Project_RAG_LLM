
import gradio as gr
import requests
import pandas as pd
import plotly.express as px 


def generate_report(symbol, question):
    url = "http://localhost:8000/rapor/generate-report"
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




def plot_stock_data(stock_data):
    stock_data['DATE'] = pd.to_datetime(stock_data['DATE'])
    fig = px.line(stock_data, x='DATE', y='CLOSING_TL', title='Stock Price Over Time', 
                  labels={'DATE': 'Date', 'CLOSING_TL': 'Closing Price (TL)'})
    fig.update_layout(template="plotly_dark", title_x=0.5)
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


