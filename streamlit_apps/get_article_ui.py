import os
import sys
import streamlit as st
import pypandoc

# Download the needed .pkg
pypandoc.download_pandoc()

# Adjusting the path to include the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

# Importing the necessary module
from get_articles import search_google, scrape_content, translate_to_farsi

# Setting up the Streamlit app
st.title("Article Translation")
st.divider()

# Initialize session state variables
if "topic" not in st.session_state:
    st.session_state.topic = ""
if "results" not in st.session_state:
    st.session_state.results = []
if "selected_article" not in st.session_state:
    st.session_state.selected_article = None

# User input for the topic
st.text_input(
    label="Enter the topic you want:",
    placeholder="self-care during pregnancy",
    key="topic"
)

# Search button
if st.button("Search"):
    with st.spinner("Searching for articles..."):
        st.session_state.results = search_google(st.session_state.topic)
        st.session_state.selected_article = None  # Reset selected article

# Display search results if available
if st.session_state.results:
    article_titles = [article["title"] for article in st.session_state.results]
    selected_title = st.selectbox(
        label="Select an article:",
        options=article_titles,
        key="selected_title"
    )
    # Update selected article based on user selection
    if st.button("Translate"):
        st.session_state.selected_article = next(
            article for article in st.session_state.results if article["title"] == selected_title
        )

# Display article content and translation if an article is selected
if st.session_state.selected_article:
    url = st.session_state.selected_article["link"]
    with st.spinner("Scraping and translating..."):
        content = scrape_content(url)
        farsi_translation = translate_to_farsi(st.session_state.topic, content)
        st.subheader("Original Article URL")
        st.write(url)
        st.subheader("Translated Content")
        st.markdown(farsi_translation)
        # Specify the output file path
        output_file = 'output.docx'
        # Convert Markdown to DOCX
        pypandoc.convert_text(farsi_translation, 'docx', format='md', outputfile=output_file)
        # print(f"Markdown content has been successfully converted to {output_file}")
        with open(output_file, "rb") as f:
            data = f.read()
        st.download_button("Download article as DOCX", data=data, file_name="translated_article.docx")

