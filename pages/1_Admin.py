import streamlit as st
from resources.utils import (load_logger)
from resources.admin import  Admin


if __name__ == "__main__":
    logger = load_logger("admin.log")
    logger.info("admin page reached")
    st.set_page_config(page_title="Admin",
                       page_icon="🛠️",
                       layout="wide",
                       initial_sidebar_state="collapsed",
                       menu_items=None,
                       )
    admin_handler = Admin(logger)
    admin_handler.admin_actions()
