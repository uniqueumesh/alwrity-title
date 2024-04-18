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
               .block-container {
                    padding-top: 0rem;
                    padding-bottom: 0rem;
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)
    st.markdown(f"""
      <style>
      [class="st-emotion-cache-7ym5gk ef3psqc12"]{{
            display: inline-block;
            padding: 5px 20px;
            background-color: #4681f4;
            color: #FBFFFF;
            width: 300px;
            height: 35px;
            text-align: center;
            text-decoration: none;
            font-size: 16px;
            border-radius: 8px;’
      }}
      </style>
    """
    , unsafe_allow_html=True)

    # Hide top header line
    hide_decoration_bar_style = '<style>header {visibility: hidden;}</style>'
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

    # Hide footer
    hide_streamlit_footer = '<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>'
    st.markdown(hide_streamlit_footer, unsafe_allow_html=True)

    # Title and description
    st.title("✍️ Alwrity - AI Blog Title Generator")

    # Input section
    with st.expander("**PRO-TIP** - Read the instructions below.", expanded=True):
        col1, col2, space = st.columns([5, 5, 0.5])
        with col1:
            input_blog_keywords = st.text_input('**Enter main keywords of your blog!** (2-3 words that define your blog)')
            input_blog_content = st.text_input('**Copy/Paste your entire blog content.** (Tip: Use Alwrity to write your blog)', 'Optional')
        with col2:
            input_title_type = st.selectbox('Blog Type', ('General', 'How-to Guides', 'Tutorials', 'Listicles', 'Newsworthy Posts', 'FAQs', 'Checklists/Cheat Sheets'), index=0)
            input_title_intent = st.selectbox('Search Intent', ('Informational Intent', 'Commercial Intent', 'Transactional Intent', 'Navigational Intent'), index=0)

    # Generate Blog Title button
    if st.button('**Generate Blog Titles**'):
        with st.spinner():
            if input_blog_content == 'Optional':
                input_blog_content = None

            # Clicking without providing data, really ?
            if (not input_blog_keywords) and (not input_blog_content):
                st.error('** 🫣Provide Inputs to generate Blog Tescription. Either Blog Keywords OR content, is required!**')
            elif input_blog_keywords or input_blog_content:
                blog_titles = generate_blog_titles(input_blog_keywords, input_blog_content, input_title_type, input_title_intent)
                if blog_titles:
                    st.subheader('**👩🧕🔬Go Rule search ranking with these Blog Titles!**')
                    with st.expander("** Final - Blog Titles Output 🎆🎇 🎇 **", expanded=True):
                        st.markdown(blog_titles)
                else:
                    st.error("💥**Failed to generate blog titles. Please try again!**")


# Function to generate blog metadesc
def generate_blog_titles(input_blog_keywords, input_blog_content, input_title_type, input_title_intent):
    """ Function to call upon LLM to get the work done. """
    # If keywords and content both are given.
    if input_blog_content and input_blog_keywords:
        prompt = f"""As a SEO expert, I will provide you with main 'blog keywords' and 'blog content'.
        Your task is write 3 SEO optimised blog titles, from given blog keywords and content.

        Follow the below guidelines for generating the blog titles:
        1). As SEO expert, follow all best practises for SEO optimised blog titles.
        2). Your response should be optimised around given keywords and content.
        3). Optimise your response for web search intent {input_title_intent}.
        4). Optimise your response for blog type of {input_title_type}.\n

        blog keywords: '{input_blog_keywords}'\n
        blog content: '{input_blog_content}'
        """
    elif input_blog_keywords and not input_blog_content:
        prompt = f"""As a SEO expert, I will provide you with main 'keywords' of a blog.
        Your task is write 3 SEO optimised blog titles from given blog keywords.

        Follow the below guidelines for generating the blog titles:
        1). As SEO expert, follow all best practises for SEO optimised blog titles.
        2). Your response should be optimised around given keywords and content.
        3). Optimise your response for web search intent {input_title_intent}.
        4). Optimise your response for blog type of {input_title_type}.\n

        blog keywords: '{input_blog_keywords}'\n
        """
    elif input_blog_content and not input_blog_keywords:
        prompt = f"""As a SEO expert, I will provide you with a 'blog content'.
        Your task is write 3 SEO optimised blog meta descriptions from given blog content.

        Follow the below guidelines for generating the blog titles:
        1). As SEO expert, follow all best practises for SEO optimised blog titles.
        2). Your response should be optimised around given keywords and content.
        3). Optimise your response for web search intent {input_title_intent}.
        4). Optimise your response for blog type of {input_title_type}.\n

        blog content: '{input_blog_content}'\n
        """
    blog_titles = gemini_text_response(prompt)
    return blog_titles



@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def gemini_text_response(prompt):
    """ Common functiont to get response from gemini pro Text. """
    try:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    except Exception as err:
        st.error(f"Failed to configure Gemini: {err}")
    # Set up the model
    generation_config = {
        "temperature": 0.6,
        "top_p": 0.3,
        "top_k": 1,
        "max_output_tokens": 1024
    }
    # FIXME: Expose model_name in main_config
    model = genai.GenerativeModel(model_name="gemini-1.0-pro", generation_config=generation_config)
    try:
        # text_response = []
        response = model.generate_content(prompt)
        return response.text
    except Exception as err:
        st.error(response)
        st.error(f"Failed to get response from Gemini: {err}. Retrying.")



if __name__ == "__main__":
    main()
