import os
import json
import argparse
import logging
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
from openai import OpenAI

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_response_from_openai(prompt, model="gpt-4o-mini", temperature=0):
    client = OpenAI(api_key=os.environ.get("IR_WN_KEY"))
    messages = [{"role": "user", "content": prompt}]
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error in OpenAI API call: {str(e)}")
        return None

def search_google(topic):
    params = {
        "engine": "google",
        "q": f"best articles about {topic}",
        "api_key": os.environ.get("SERP_API_KEY")
    }
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        return results["organic_results"][:3]
    except Exception as e:
        logging.error(f"Error in Google search: {str(e)}")
        return []

def scrape_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Remove navigation, footer, scripts, and styles to avoid irrelevant content
    for tag in soup(['nav', 'footer', 'script', 'style']):
        tag.decompose()
    
    # Extract text from <p>, <li>, <h1>, <h2>, and <h3> tags
    selected_tags = soup.find_all(['p', 'li', 'h1', 'h2', 'h3'])
    content = ' '.join([tag.get_text(strip=True) for tag in selected_tags])
    
    return content

def translate_to_farsi(topic, content):
    prompt = f"""
    I have scraped HTML content about "{topic}".
    Please translate it into fluent Farsi, ensuring it's well-formatted and stylistically appropriate for an Iranian audience.
    Make sure to adapt any phrases, examples, or references to better suit the cultural context of Iranian users.

    Here is the content:
    `{content}`
    """
    translated = get_response_from_openai(prompt, temperature=0.7)
    if translated:
        logging.info(f"Content translated to Farsi successfully for topic: {topic}")
    else:
        logging.warning(f"Failed to translate content to Farsi for topic: {topic}")
    return translated

def process_article(result, topic):
    logging.info(f"Processing article: {result['link']}")
    content = scrape_content(result['link'])
    farsi_content = translate_to_farsi(topic, content)
    return {
        'url': result['link'],
        'farsi_content': farsi_content
    }

def main():
    parser = argparse.ArgumentParser(description='Search and translate articles on a given topic.')
    parser.add_argument('--topic', type=str, required=True, help='The topic to search for')
    args = parser.parse_args()

    topic = args.topic
    logging.info(f"Starting search for topic: {topic}")
    top_results = search_google(topic)
    
    articles = [process_article(result, topic) for result in top_results]

    logging.info(f"Completed processing for topic: {topic}")
    return json.dumps(articles, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    print(main())
