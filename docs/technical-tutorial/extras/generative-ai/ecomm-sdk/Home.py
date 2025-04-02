import streamlit as st
import pandas as pd
import practicuscore as prt
from practicuscore.gen_ai import PrtLangMessage, PrtLangRequest
import requests


st.set_page_config(page_title="E-Commerce Product Review & Chatbot", layout="wide")

def load_data():
    excel_file = "ecommerce_data_with_images.xlsx"
    products_df = pd.read_excel(excel_file, sheet_name="Products")
    reviews_df = pd.read_excel(excel_file, sheet_name="Reviews")
    sizes_df = pd.read_excel(excel_file, sheet_name="Sizes")
    images_df = pd.read_excel(excel_file, sheet_name="ProductImages")
    return products_df, reviews_df, sizes_df, images_df

products_df, reviews_df, sizes_df, images_df = load_data()

st.title("🛍️ E-Commerce Product Review & Chatbot")

col1, col2 = st.columns([3, 1])
with col1:
    selected_product = st.selectbox("Select a product:", products_df["product_name"].unique())
with col2:
    show_image = st.button("Show Image")

if show_image and selected_product:
    product_id = products_df.loc[products_df["product_name"] == selected_product, "product_id"].values[0]
    image_url = images_df.loc[images_df["product_id"] == product_id, "image_url"].values[0]
    st.image(image_url, caption=selected_product, width=300)

selected_rating = st.slider("Filter reviews by rating:", min_value=1, max_value=5, value=(1, 5))

if selected_product:
    product_id = products_df.loc[products_df["product_name"] == selected_product, "product_id"].values[0]
    product_reviews = reviews_df[(reviews_df["product_id"] == product_id) & (reviews_df["rating"].between(selected_rating[0], selected_rating[1]))]
    available_sizes = sizes_df["size"].unique()
    
    st.subheader("Customer Reviews")
    review_columns = st.columns(2)
    
    for i, (_, row) in enumerate(product_reviews.iterrows()):
        with review_columns[i % 2]:
            st.markdown(
                f"""
                <div style='padding: 10px; border-radius: 10px; background-color: #2c3e50; color: #ecf0f1; margin-bottom: 10px;'>
                    <strong>⭐ {row['rating']}/5</strong><br>
                    {row['review']}
                </div>
                """, unsafe_allow_html=True)
    
    st.subheader("Available Sizes")
    st.write(", ".join(available_sizes))

import time

def analyze_sentiment(reviews):
    if reviews.empty:
        return ["No reviews available."]

    api_url = f"https://dev.practicus.io/models/llm-proxy/"
    token = prt.models.get_session_token(api_url=api_url)

    context = f"You are an expert product assistant providing details about e-commerce products based on available data.\nReviews: {', '.join(reviews['review'].tolist())}"

    practicus_llm_req = PrtLangRequest(
        messages=[PrtLangMessage(content=context, role="human")],
        lang_model='model',
        streaming=True
    )

    headers = {
        'authorization': f'Bearer {token}',
        'content-type': 'application/json'
    }

    data_js = practicus_llm_req.model_dump_json(indent=2, exclude_unset=True)

    results = []


    placeholder = st.empty()

    with requests.post(api_url, headers=headers, data=data_js, stream=True) as r:
        for word in r.iter_content(1024):

            word_decoded = word.decode("utf-8")
            results.append(word_decoded)

            placeholder.markdown("".join(results))


            time.sleep(0.1)


    return "".join(results)


def analyze_sentiment2(reviews):
    if reviews.empty:
        return ["No reviews available."]

    api_url = f"https://dev.practicus.io/models/llm-proxy/"
    token = prt.models.get_session_token(api_url=api_url)

    context = f"Based on the response above, which specific parts of the reviews contributed to the answer? Please extract relevant quotes.\nReviews: {', '.join(product_reviews['review'].tolist()[:10])}"

    practicus_llm_req = PrtLangRequest(
        messages=[PrtLangMessage(content=context, role="human")],
        lang_model='model',
        streaming=True
    )

    headers = {
        'authorization': f'Bearer {token}',
        'content-type': 'application/json'
    }

    data_js = practicus_llm_req.model_dump_json(indent=2, exclude_unset=True)

    results = []


    placeholder = st.empty()

    with requests.post(api_url, headers=headers, data=data_js, stream=True) as r:
        for word in r.iter_content(1024):

            word_decoded = word.decode("utf-8")
            results.append(word_decoded)
            

            placeholder.markdown("".join(results))


            time.sleep(0.1)


    return "".join(results)


st.sidebar.title("🗨️ Chat with AI Product Assistant")
user_input = st.sidebar.text_input("Ask about the product:")
if user_input:
    
    sentiment_summary = analyze_sentiment(product_reviews)
    st.sidebar.write(sentiment_summary)
    st.sidebar.subheader("🔍 Relevant Context from Reviews")

    sentiment_summary2 = analyze_sentiment2(product_reviews)
    st.sidebar.write(sentiment_summary2)


st.sidebar.subheader("💡 Suggested Questions")
if selected_product:
    context = f"Product: {selected_product}\nReviews: {', '.join(product_reviews['review'].tolist())}"
    suggested_questions = [
        "What is the overall customer satisfaction for this product?",
        "Are there any common complaints about this product?",
        "What do most customers like about this product?"
    ]
    for question in suggested_questions:
        st.sidebar.write(f"- {question}")
