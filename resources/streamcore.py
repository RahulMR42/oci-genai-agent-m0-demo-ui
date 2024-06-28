import os
import oci
import shortuuid
import uuid
import streamlit as st
from streamlit_feedback import streamlit_feedback
import genai_agent_service_bmc_python_client
from resources.utils import (return_keys_from_endpoint_config,
                             fetch_endpoint_ocid)

class Agent:
    def __init__(self):
        self.CONFIG_PROFILE = os.getenv("oci_config_profile", default="DEFAULT")
        self.oci_config = oci.config.from_file()
        self.agent_base_url = os.environ["oci_agent_base_url"]

    @staticmethod
    def init_chat_history():
        st.session_state["session_uuid"] = f"{str(uuid.uuid4())}"
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "session_id" not in st.session_state:
            st.session_state.session_id = None


    def create_oci_client(self):
        oci_client = genai_agent_service_bmc_python_client.GenerativeAiAgentRuntimeClient(
            config=self.oci_config,
            service_endpoint=self.agent_base_url,
            retry_strategy=oci.retry.NoneRetryStrategy(),
            timeout=(10, 240))
        return oci_client


    @staticmethod
    def sidebar_message():
        st.sidebar.markdown(
            """
            ### About.
            A simple UI to call [OCI Genai Agent endpoints](https://docs.oracle.com/en-us/iaas/Content/generative-ai-agents/home.htm)
            ### Credits.
            - **Created by rahul.m.r@oracle.com**.
            - **Inspired from - [cgpavlakos](https://github.com/cgpavlakos/genai_agent/tree/main)**.
            """
        )


    def sidebar(self):
        with st.sidebar:
            list_of_keys = return_keys_from_endpoint_config()
            selection = st.sidebar.selectbox("Select Endpoint", list_of_keys)
            if selection == "Custom":
                agent_endpoint = st.text_input("Enter an Agent OCID")
            else:
                agent_endpoint = fetch_endpoint_ocid(selection)
            os.environ['agent_endpoint'] = agent_endpoint
            col1, col2 = st.columns([1,1])
            with col1:
                if st.button("🔄 Re-run", type="primary", use_container_width=False, help="Reset chat history/Update Endpoint"):
                    st.session_state.messages = []
                    st.session_state.session_id = None
                    st.rerun()
            with col2:
                data = str(st.session_state)
                filename =  f"session_histroy_{shortuuid.ShortUUID().random(length=6)}.txt"
                if st.download_button("⬇️ Download", data, filename, use_container_width=False, help="Download Chat histroy with feedback"):
                    pass
            self.sidebar_message()
            self.agent_footer()

    def agent_feedback(self):
            st.toast("Feedback saved.",icon="✔️")
    def agent_footer(self):
        footer = """<style>.footer {position: fixed;left: 0;bottom: 0;width: 100%;
                 background-color: #F0F0F0;color: black;text-align: center;}
                </style><div class='footer'><p> 🏷️ 0.0.0b | 🅾️ Powered by OCI Genai Agent | ©️ - Oracle 2024  </p></div>"""
        st.markdown(footer, unsafe_allow_html=True)

    def agent_load(self, display_name, description, stream_option):
        self.sidebar()
        agent_endpoint = os.environ['agent_endpoint']
        st.info(f"🔍 Agent {agent_endpoint} joined the Chat ..")
        if st.session_state.session_id is None:
            agent_oci_client = self.create_oci_client()
            session_attributes = genai_agent_service_bmc_python_client.models.CreateSessionDetails(
                display_name=display_name, idle_timeout_in_seconds=10, description=description
            )
            session_response = agent_oci_client.create_session(session_attributes, agent_endpoint)
            st.session_state.session_id = session_response.data.id
            if hasattr(session_response.data, 'welcome_message'):
                st.session_state.messages.append({"role": "assistant", "content": session_response.data.welcome_message})
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        # Get user input
        if user_input := st.chat_input("How can I help you .. "):
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user", avatar="💬"):
                st.markdown(user_input)
            with st.spinner():
                execute_session_details = genai_agent_service_bmc_python_client.models.ExecuteSessionDetails(user_message = str(user_input), should_stream=stream_option)
                agent_oci_client = self.create_oci_client()
                execute_session_response = agent_oci_client.execute_session(agent_endpoint, st.session_state.session_id, execute_session_details)
            if execute_session_response.status == 200:
                response_content = execute_session_response.data.message.content
                st.session_state.messages.append({"role": "assistant", "content": response_content.text})
                with st.chat_message("assistant"):
                    st.markdown(response_content.text)
                if response_content.citations:
                    with st.expander("Citations"):
                        for i, citation in enumerate(response_content.citations, start=1):
                            st.write(f"**Citation {i}:**")  # Add citation number
                            st.markdown(f"**Source:** [{citation.source_location.url}]({citation.source_location.url})")
                            st.text_area("Citation Text", value=citation.source_text, height=200)
                with st.form('form'):
                    streamlit_feedback(feedback_type="thumbs",
                                       optional_text_label="[Optional] Please provide an explanation",
                                       align="flex-start",
                                       key='fb_k')
                    st.form_submit_button('Save feedback', on_click=self.agent_feedback)











