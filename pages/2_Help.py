import streamlit as st
from resources.helper import help_images
if __name__ == "__main__":
    st.set_page_config(page_title="Help",
                   page_icon="📌",
                   layout="wide",
                   initial_sidebar_state="collapsed",
                   menu_items=None,
                   )
    help_images()



