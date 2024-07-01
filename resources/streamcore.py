import os
import oci
import shortuuid
import uuid
import streamlit as st
from streamlit_feedback import streamlit_feedback
import genai_agent_service_bmc_python_client
from resources.utils import (return_keys_from_endpoint_config,
                             fetch_endpoint_ocid,
                             set_region)

class Agent:
    def __init__(self, logger):
        self.CONFIG_PROFILE = os.getenv("oci_config_profile", default="DEFAULT")
        self.oci_config = oci.config.from_file()
        self.logger = logger


    def init_chat_history(self):
        self.logger.info("Initiating chat ui")
        st.session_state["session_uuid"] = f"{str(uuid.uuid4())}"
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "session_id" not in st.session_state:
            st.session_state.session_id = None
            self.logger.info("Invalidating session ID")

    def create_oci_client(self, region):
        oci_client = genai_agent_service_bmc_python_client.GenerativeAiAgentRuntimeClient(
            config=self.oci_config,
            service_endpoint=os.environ['oci_agent_base_url'],
            retry_strategy=oci.retry.NoneRetryStrategy(),#oci.retry.NoneRetryStrategy(), #oci.retry.NoneRetryStrategy(),
            region=region,
            timeout=(10, 240))
        self.logger.info("Starting new OCI client")
        return oci_client


    @staticmethod
    def sidebar_message():
        st.sidebar.markdown(
            """
            ### About.
            A simple UI to call [OCI Genai Agent endpoints](https://docs.oracle.com/en-us/iaas/Content/generative-ai-agents/home.htm)
            ### Credits.
            - **Creator - rahul.m.r@oracle.com**.
            - **Inspirations (UI)** 
            - chris.pavlakos@oracle.com
            - shujie.chen@oracle.com
            - prabhat.kumar.prabhakar@oracle.com
            
            
            
            """
        )

    def session_exit(self, agent_oci_client):
        try:
            if st.session_state.session_id is not None:
                agent_endpoint = os.environ['agent_endpoint']
                self.logger.info("Attempting session exit")
                delete_session_response = agent_oci_client.delete_session(agent_endpoint, st.session_state.session_id)
                self.logger.info(f"Logout done - {str(delete_session_response.data)}/{str(delete_session_response.status)}")
        except Exception as error:
            self.logger.error(f"Logout failed - {error}")


    def logout(self,agent_oci_client):
        col1, col2, col3 = st.columns([2,2,2])
        with col2:
            if st.button("【⏻]", use_container_width=False, help="Delete Chat Session"):
                self.logger.info("Attempting chat session deletion")
                self.session_exit(agent_oci_client)

    def sidebar(self):
        agent_endpoint = os.environ['agent_endpoint']
        region = set_region(agent_endpoint)
        agent_oci_client = self.create_oci_client(region)
        with st.sidebar:
            list_of_keys = return_keys_from_endpoint_config()
            selection = st.sidebar.selectbox("Select Endpoint", list_of_keys)
            self.logger.info("Got list of keys")
            if selection == "Custom":
                agent_endpoint = st.text_input("Enter an Agent OCID",value="")
            else:
                agent_endpoint = fetch_endpoint_ocid(selection)
            os.environ['agent_endpoint'] = agent_endpoint
            self.logger.info(f"Loading with endpoint {os.environ['agent_endpoint']}")
            col1, col2, col3 = st.columns([1,1,1])
            with col1:
                if st.button("🔄", type="secondary", use_container_width=True, help="Reset chat history/Update Endpoint"):
                    st.session_state.messages = []
                    st.session_state.session_id = None
                    self.logger.info("Reloading the chat.")
                    self.session_exit(agent_oci_client)
                    st.rerun()
            with col2:
                data = str(st.session_state)
                filename =  f"session_histroy_{shortuuid.ShortUUID().random(length=6)}.txt"
                if st.download_button("⬇️", data, filename, use_container_width=True, help="Download Chat histroy with feedback"):
                    self.logger.info(f"Downloaded chat history {filename}")

            self.sidebar_message()
            self.logout(agent_oci_client)
            self.agent_footer()

    def warning_message(self, message):
        self.logger.info(f"Warning message invoked - {message}")
        st.warning(message, icon="⚠️")

    def agent_feedback(self):
        st.toast("Feedback saved.",icon="✔️")
        self.logger.info(f"Feedback received for f{st.session_state.session_id}")

    @staticmethod
    def agent_footer():
        footer = """<style>.footer {position: fixed;left: 0;bottom: 0;width: 100%;
                 background-color: #F0F0F0;color: black;text-align: center;}
                </style><div class='footer'><p> 🏷️ 0.0.0b | 🅾️ Powered by OCI Genai Agent | ©️ - Oracle 2024  </p></div>"""
        st.markdown(footer, unsafe_allow_html=True)

    def agent_load(self, display_name, description, stream_option):
        agent_endpoint = os.environ['agent_endpoint']
        self.logger.info(f"Loading agent with {os.environ['agent_endpoint']}")
        region = set_region(agent_endpoint)
        self.logger.info(f"Using oci region {region}")
        st.info(f"🔍 Agent {agent_endpoint} joined the Chat ..")
        self.sidebar()
        if st.session_state.session_id is None:
            agent_oci_client = self.create_oci_client(region)
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
                self.logger.info("Attempting execution ..")
                execute_session_details = genai_agent_service_bmc_python_client.models.ExecuteSessionDetails(user_message = str(user_input), should_stream=stream_option)
                agent_oci_client = self.create_oci_client(region)
                execute_session_response = agent_oci_client.execute_session(agent_endpoint, st.session_state.session_id, execute_session_details)
            if execute_session_response.status == 200:
                self.logger.info(f"Received API output with return as 200")
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
            else:
                self.logger.error(f"API execution failed with error {execute_session_response.status}")
