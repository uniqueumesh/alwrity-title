import time #Iwish
import os
import json
import streamlit as st
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
import pandas as pd
import io


def main():
    # Set page configuration
    st.set_page_config(
        page_title="Alwrity",
        layout="wide",
    )
    # Remove the extra spaces from margin top.
    st.markdown("""
        <style>
        ::-webkit-scrollbar-track {
        background: #e1ebf9;
        }

        ::-webkit-scrollbar-thumb {
            background-color: #90CAF9;
            border-radius: 10px;
            border: 3px solid #e1ebf9;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #64B5F6;
        }

        ::-webkit-scrollbar {
            width: 16px;
        }
        div.stButton > button:first-child {
            background: #1565C0;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 10px 2px;
            cursor: pointer;
            transition: background-color 0.3s ease;
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
            font-weight: bold;
        }
        </style>
    """
    , unsafe_allow_html=True)

    # Hide top header line
    hide_decoration_bar_style = '<style>header {visibility: hidden;}</style>'
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

    # Hide footer
    hide_streamlit_footer = '<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>'
    st.markdown(hide_streamlit_footer, unsafe_allow_html=True)

    st.title("✍️ Alwrity - AI Blog Title Generator")

    # --- API Key Input Section (moved below title) ---
    with st.expander("API Configuration 🔑", expanded=False):
        st.markdown('''If the default Gemini API key is unavailable or exceeds its limits, you can provide your own API key below.<br>
        <a href="https://aistudio.google.com/app/apikey" target="_blank">Get Gemini API Key</a><br>
        <a href="https://serper.dev" target="_blank">Get SERPER API Key</a>
        ''', unsafe_allow_html=True)
        user_gemini_api_key = st.text_input("Gemini API Key", type="password", help="Paste your Gemini API Key here if you have one. Otherwise, the tool will use the default key if available.")
        user_serper_api_key = st.text_input("Serper API Key (for SERP research)", type="password", help="Paste your Serper API Key here if you have one. Otherwise, the tool will use the default key if available.")

    # Input section
    with st.expander("**PRO-TIP** - Follow the steps below for best results.", expanded=True):
        col1, col2 = st.columns([5, 5])

        with col1:
            input_blog_keywords = st.text_input(
                '**🔑 Enter main keywords of your blog!**',
                placeholder="e.g., AI tools, digital marketing, SEO",
                help="Use 2-3 words that best describe the main topic of your blog."
            )
            input_blog_content = st.text_area(
                '**📄 Copy/Paste your entire blog content.** (Optional)',
                placeholder="e.g., Content about the importance of AI in digital marketing...",
                help="Paste your full blog content here for more accurate title suggestions. This is optional."
            )

        with col2:
            input_title_type = st.selectbox(
                '📝 Blog Type', 
                ('General', 'How-to Guides', 'Tutorials', 'Listicles', 'Newsworthy Posts', 'FAQs', 'Checklists/Cheat Sheets'),
                index=0
            )
            input_title_intent = st.selectbox(
                '🔍 Search Intent', 
                ('Informational Intent', 'Commercial Intent', 'Transactional Intent', 'Navigational Intent'), 
                index=0
            )
            language_options = ["English", "Spanish", "French", "German", "Chinese", "Japanese", "Other"]
            input_language = st.selectbox(
                '🌐 Select Language', 
                options=language_options,
                index=0,
                help="Choose the language for your blog title."
            )
            if input_language == "Other":
                input_language = st.text_input(
                    'Specify Language', 
                    placeholder="e.g., Italian, Dutch",
                    help="Specify your preferred language."
                )
            # Add Target Audience input
            input_audience = st.text_input(
                '🎯 Target Audience (Optional)',
                placeholder="e.g., for Marketers, for Small Businesses",
                help="Specify your target audience for more tailored titles."
            )

    # --- SERP Competitor Title Research ---
    serp_titles = []
    serp_cache_key = f"serp_{input_blog_keywords}_{user_serper_api_key}"
    if input_blog_keywords:
        if serp_cache_key in st.session_state:
            serp_titles = st.session_state[serp_cache_key]
        else:
            serp_titles = get_serp_competitor_titles(input_blog_keywords, user_serper_api_key)
            st.session_state[serp_cache_key] = serp_titles
        if serp_titles == 'RATE_LIMIT':
            st.warning('⚠️ Serper API rate limit or quota exceeded. Please try again later or use a different API key.')
            serp_titles = []
        elif serp_titles:
            st.markdown('<h4 style="margin-top:1.5rem; color:#1976D2;">🔎 Top 10 Competitor Blog Titles from Google SERP</h4>', unsafe_allow_html=True)
            selected_title = st.selectbox('View a competitor title:', serp_titles, help="These are the top 10 blog titles from Google for your keyword. Use them for inspiration or comparison.")
        else:
            st.info('No competitor titles found for your keyword. Check your Serper API key or try a different keyword.')

    # Add option for number of titles
    st.markdown('<h3 style="margin-top:2rem;">How many blog titles do you want to generate?</h3>', unsafe_allow_html=True)
    num_titles = st.slider('Number of SEO-optimized blog titles', min_value=1, max_value=10, value=5, help="Choose how many blog titles to generate (1-10).")

    # Generate Blog Title button
    if st.button('**Generate Blog Titles**'):
        with st.spinner("Generating blog titles..."):
            if input_blog_content == 'Optional':
                input_blog_content = None

            if not input_blog_keywords and not input_blog_content:
                st.error('**🫣 Provide Inputs to generate Blog Titles. Either Blog Keywords OR content is required!**')
            else:
                blog_titles = generate_blog_titles(
                    input_blog_keywords, input_blog_content, input_title_type, input_title_intent, input_language, user_gemini_api_key, num_titles, input_audience
                )
                if blog_titles:
                    st.session_state['blog_titles'] = blog_titles
                else:
                    st.error("💥 **Failed to generate blog titles. Please try again!**")
            st.markdown(st.session_state['blog_titles'])
            # Excel export for A/B testing
            titles_list = [t.strip().lstrip('0123456789. ') for t in st.session_state['blog_titles'].split('\n') if t.strip()]
            df = pd.DataFrame({'Blog Title': titles_list})
            excel_buffer = io.BytesIO()
            df.to_excel(excel_buffer, index=False, engine='openpyxl')
            excel_buffer.seek(0)
            st.download_button(
                label="Download Titles as Excel for A/B Testing",
                data=excel_buffer,
                file_name="blog_titles.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


# Function to generate blog metadesc
def generate_blog_titles(input_blog_keywords, input_blog_content, input_title_type, input_title_intent, input_language, user_gemini_api_key=None, num_titles=5, input_audience=None):
    """ Function to call upon LLM to get the work done. """
    # Get competitor titles for inspiration (use cache if available)
    competitor_titles = []
    serp_cache_key = f"serp_{input_blog_keywords}_{os.getenv('SERPER_API_KEY') or ''}"
    if input_blog_keywords and serp_cache_key in st.session_state:
        competitor_titles = st.session_state[serp_cache_key] if st.session_state[serp_cache_key] != 'RATE_LIMIT' else []
    elif input_blog_keywords:
        competitor_titles = get_serp_competitor_titles(input_blog_keywords)
    competitor_titles_str = '\n'.join(competitor_titles) if competitor_titles else ''
    # Improved, simple prompt for best SEO practices
    seo_guidelines = f"""
Generate {num_titles} different blog post titles for the topic below.

Rules:
- Use the main keyword in each title.
- Make each title unique and interesting.
- Keep each title between 50 and 65 characters.
- Use simple, clear language.
- Try different styles: questions, lists, how-to, guides, or tips.
- Add numbers or power words if it makes sense.
- Do not copy from the competitor titles below.
- Make sure the titles fit the blog type: {input_title_type}.
- Match the search intent: {input_title_intent}.
- Write in this language: {input_language}.
- If a target audience is given, make the titles fit that audience.

Topic/Keywords: {input_blog_keywords}
Blog Content (if any): {input_blog_content}
Target Audience (if any): {input_audience}
Competitor Titles (for inspiration, do not copy):
{competitor_titles_str}

List only the {num_titles} titles. Do not add anything else.
"""
    competitor_section = ""  # Now included in the main prompt
    if input_blog_content and input_blog_keywords:
        prompt = seo_guidelines
    elif input_blog_keywords and not input_blog_content:
        prompt = seo_guidelines
    elif input_blog_content and not input_blog_keywords:
        prompt = seo_guidelines
    blog_titles = gemini_text_response(prompt, user_gemini_api_key)
    if blog_titles == 'RATE_LIMIT':
        st.warning('⚠️ Gemini API rate limit or quota exceeded. Please try again later or use a different API key.')
        return None
    return blog_titles


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def gemini_text_response(prompt, user_gemini_api_key=None):
    import google.generativeai as genai
    import os
    try:
        api_key = user_gemini_api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            st.error("GEMINI_API_KEY is missing. Please provide it in the API Configuration section or set it in the environment.")
            return None
        genai.configure(api_key=api_key)
    except Exception as err:
        st.error(f"Failed to configure Gemini: {err}")
        return None
    generation_config = {
        "temperature": 0.6,
        "top_p": 0.3,
        "top_k": 1,
        "max_output_tokens": 1024
    }
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)
    try:
        response = model.generate_content(prompt)
        if hasattr(response, 'code') and response.code == 429:
            return 'RATE_LIMIT'
        if hasattr(response, 'text') and ('rate limit' in response.text.lower() or 'quota' in response.text.lower()):
            return 'RATE_LIMIT'
        return response.text
    except Exception as err:
        if 'quota' in str(err).lower() or 'rate limit' in str(err).lower():
            return 'RATE_LIMIT'
        st.error(f"Failed to get response from Gemini: {err}. Retrying.")
        return None


def get_serp_competitor_titles(search_keywords, user_serper_api_key=None):
    import requests
    import json
    import os
    try:
        serper_api_key = user_serper_api_key or os.getenv('SERPER_API_KEY')
        if not serper_api_key:
            return []
        url = "https://google.serper.dev/search"
        payload = json.dumps({
            "q": search_keywords,
            "gl": "us",
            "hl": "en",
            "num": 10,
            "autocorrect": True,
            "page": 1,
            "type": "search",
            "engine": "google"
        })
        headers = {
            'X-API-KEY': serper_api_key,
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 429 or 'rate limit' in response.text.lower() or 'quota' in response.text.lower():
            return 'RATE_LIMIT'
        if response.status_code == 200:
            data = response.json()
            titles = []
            for item in data.get('organic', [])[:10]:
                title = item.get('title')
                if title:
                    titles.append(title)
            return titles
        else:
            return []
    except Exception:
        return []


if __name__ == "__main__":
    main()
