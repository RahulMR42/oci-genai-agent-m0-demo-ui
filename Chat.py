import os
import streamlit as st
from resources.streamauth import check_password
from resources.streamcore import Agent
from resources.utils import (fetch_endpoint_ocid,
                             load_env,
                             load_logger)
#
def cred_check(logger):
    st.set_page_config(page_title="GenaiAgent",
                       page_icon="💬",
                       layout="wide",
                       initial_sidebar_state="collapsed",
                       menu_items=None)
    if not check_password():
        logger.error("Credential error")
        st.stop()
    #Main Streamlit app starts here
    logger.info("Starting app")
    load_env()

def agent_action(agent_handler, stream_option, display_name, description,default_key, logger):
    logger.info("Starting init function")
    agent_handler.init_chat_history()
    default_agent_endpoint = fetch_endpoint_ocid(default_key)
    logger.info(f"Using endpoint {default_agent_endpoint} to load the application")
    os.environ["agent_endpoint"] = os.getenv("agent_endpoint",default=default_agent_endpoint)
    agent_handler.agent_load(display_name, description, stream_option)


if __name__ == "__main__":
    stream_option = False   #Enable Stream
    default_key = os.getenv('default_key',default="Chat")#"Chat"  # Default endpoint key for endpoint ocid
    logger = load_logger("chat.log")
    cred_check(logger)
    agent_handler = Agent(logger)
    agent_action(agent_handler, stream_option, "m0-genaisolution", "Demo of Agent M0", default_key, logger)
