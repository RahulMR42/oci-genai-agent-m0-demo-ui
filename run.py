import os
import streamlit as st
from resources.streamauth import check_password
from resources.streamcore import Agent
from resources.utils import (fetch_endpoint_ocid,
                             load_env)
#
def cred_check():
    st.set_page_config(page_title="GenaiAgent",
                       page_icon="💬",
                       layout="wide",
                       initial_sidebar_state="collapsed",
                       menu_items=None)
    if not check_password():
        st.stop()
    #Main Streamlit app starts here
    load_env()

def agent_action(agent_handler, stream_option, display_name, description,default_key):
    agent_handler.init_chat_history()
    default_agent_endpoint = fetch_endpoint_ocid(default_key)
    os.environ["agent_endpoint"] = default_agent_endpoint
    agent_handler.agent_load(display_name, description, stream_option)


if __name__ == "__main__":
    stream_option = False   #Enable Stream
    default_key = "Chat"  # Default endpoint key for endpoint ocid
    cred_check()
    agent_handler = Agent()
    agent_action(agent_handler, stream_option, "m0-genaisolution", "Demo of Agent M0", default_key)
