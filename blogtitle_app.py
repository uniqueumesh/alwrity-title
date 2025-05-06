import time #Iwish
import os
import json
import streamlit as st
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
import google.generativeai as genai


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

    # --- API Key Input Section ---
    with st.expander("API Configuration 🔑", expanded=False):
        st.markdown('''If the default Gemini API key is unavailable or exceeds its limits, you can provide your own API key below.<br>
        <a href="https://aistudio.google.com/app/apikey" target="_blank">Get Gemini API Key</a>
        ''', unsafe_allow_html=True)
        user_gemini_api_key = st.text_input("Gemini API Key", type="password", help="Paste your Gemini API Key here if you have one. Otherwise, the tool will use the default key if available.")

    st.title("✍️ Alwrity - AI Blog Title Generator")

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

    # Generate Blog Title button
    if st.button('**Generate Blog Titles**'):
        with st.spinner("Generating blog titles..."):
            if input_blog_content == 'Optional':
                input_blog_content = None

            if not input_blog_keywords and not input_blog_content:
                st.error('**🫣 Provide Inputs to generate Blog Titles. Either Blog Keywords OR content is required!**')
            else:
                blog_titles = generate_blog_titles(input_blog_keywords, input_blog_content, input_title_type, input_title_intent, input_language, user_gemini_api_key)
                if blog_titles:
                    st.subheader('**👩🧕🔬 Go Rule search ranking with these Blog Titles!**')
                    with st.expander("**Final - Blog Titles Output 🎆🎇🎇**", expanded=True):
                        st.markdown(blog_titles)
                else:
                    st.error("💥 **Failed to generate blog titles. Please try again!**")


# Function to generate blog metadesc
def generate_blog_titles(input_blog_keywords, input_blog_content, input_title_type, input_title_intent, input_language, user_gemini_api_key=None):
    """ Function to call upon LLM to get the work done. """
    # If keywords and content both are given.
    if input_blog_content and input_blog_keywords:
        prompt = f"""As a SEO expert, I will provide you with main 'blog keywords' and 'blog content'.
        Your task is write 5 SEO optimised blog titles, from given blog keywords and content.

        Follow the below guidelines for generating the blog titles:
        1). As SEO expert, follow all best practises for SEO optimised blog titles.
        2). Your response should be optimised around given keywords and content.
        3). Optimise your response for web search intent {input_title_intent}.
        4). Optimise your response for blog type of {input_title_type}.
        5). Your blog titles should in {input_language} language.\n

        blog keywords: '{input_blog_keywords}'\n
        blog content: '{input_blog_content}'
        """
    elif input_blog_keywords and not input_blog_content:
        prompt = f"""As a SEO expert, I will provide you with main 'keywords' of a blog.
        Your task is write 5 SEO optimised blog titles from given blog keywords.

        Follow the below guidelines for generating the blog titles:
        1). As SEO expert, follow all best practises for SEO optimised blog titles.
        2). Your response should be optimised around given keywords and content.
        3). Optimise your response for web search intent {input_title_intent}.
        4). Optimise your response for blog type of {input_title_type}.
        5). Your blog titles should in {input_language} language.\n

        blog keywords: '{input_blog_keywords}'\n
        """
    elif input_blog_content and not input_blog_keywords:
        prompt = f"""As a SEO expert, I will provide you with a 'blog content'.
        Your task is write 5 SEO optimised blog titles from given blog content.

        Follow the below guidelines for generating the blog titles:
        1). As SEO expert, follow all best practises for SEO optimised blog titles.
        2). Your response should be optimised around given keywords and content.
        3). Optimise your response for web search intent {input_title_intent}.
        4). Optimise your response for blog type of {input_title_type}.
        5). Your blog titles should in {input_language} language.\n

        blog content: '{input_blog_content}'\n
        """
    blog_titles = gemini_text_response(prompt, user_gemini_api_key)

    return blog_titles


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def gemini_text_response(prompt, user_gemini_api_key=None):
    """ Common function to get response from gemini pro Text. """
    try:
        api_key = user_gemini_api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            st.error("GEMINI_API_KEY is missing. Please provide it in the API Configuration section or set it in the environment.")
            return None
        genai.configure(api_key=api_key)
    except Exception as err:
        st.error(f"Failed to configure Gemini: {err}")
        return None
    # Set up the model
    generation_config = {
        "temperature": 0.6,
        "top_p": 0.3,
        "top_k": 1,
        "max_output_tokens": 1024
    }
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as err:
        st.error(f"Failed to get response from Gemini: {err}. Retrying.")
        return None


if __name__ == "__main__":
    main()
