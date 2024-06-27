import os
import oci
import hmac

import streamlit as st
import genai_agent_service_bmc_python_client

# OCI Configuration
CONFIG_PROFILE = os.environ["oci_config_profile"]
config = oci.config.from_file()
endpoint = os.environ["oci_agent_base_url"]
agent_endpoint_id = os.environ["oci_agent_endpoint"]
#ocid1.genaiagentendpoint.oc1.us-chicago-1.amaaaaaafigrwqya27wppncqffppk4wdeertiaxt46y3dunqwox4a27x3qeq
#"ocid1.genaiagentendpoint.oc1.us-chicago-1.amaaaaaafigrwqyarfhk4nkxg2x6mizfcojh5fzgqbabserm5yjqk44rocma"
# Initialize chat history and session ID in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# Create GenAI Agent Runtime Client (only if session_id is None)
if st.session_state.session_id is None:
    genai_agent_runtime_client = genai_agent_service_bmc_python_client.GenerativeAiAgentRuntimeClient(
        config=config,
        service_endpoint=endpoint,
        retry_strategy=oci.retry.NoneRetryStrategy(),
        timeout=(10, 240)
    )

    # Create session
    create_session_details = genai_agent_service_bmc_python_client.models.CreateSessionDetails(
        display_name="display_name", idle_timeout_in_seconds=10, description="description"
    )
    create_session_response = genai_agent_runtime_client.create_session(create_session_details, agent_endpoint_id)

    # Store session ID
    st.session_state.session_id = create_session_response.data.id

    # Check if welcome message exists and append to message history
    if hasattr(create_session_response.data, 'welcome_message'):
        st.session_state.messages.append({"role": "assistant", "content": create_session_response.data.welcome_message})

# Streamlit UI
st.set_page_config(page_title="GenaiAgent",
                   page_icon="💬",
                   layout="wide",
                   initial_sidebar_state="collapsed",
                   menu_items=None)

def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


if not check_password():
    st.stop()


# Main Streamlit app starts here
st.title("OCI Agent - Demo")

# Display chat messages from history (including initial welcome message, if any)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
# Get user input
if user_input := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    # Create GenAI Agent Runtime Client (only if session_id is None)
    if st.session_state.session_id is None:
        genai_agent_runtime_client = genai_agent_service_bmc_python_client.GenerativeAiAgentRuntimeClient(
            config=config,
            service_endpoint=endpoint,
            retry_strategy=oci.retry.NoneRetryStrategy(),
            timeout=(10, 240)
        )

        # Create session
        create_session_details = genai_agent_service_bmc_python_client.models.CreateSessionDetails(
            display_name="display_name", idle_timeout_in_seconds=10, description="description"
        )
        create_session_response = genai_agent_runtime_client.create_session(create_session_details, agent_endpoint_id)
        st.session_state.session_id = create_session_response.data.id

    # Execute session (re-use the existing session)
    genai_agent_runtime_client = genai_agent_service_bmc_python_client.GenerativeAiAgentRuntimeClient(
        config=config,
        service_endpoint=endpoint,
        retry_strategy=oci.retry.NoneRetryStrategy(),
        timeout=(10, 240)
    )

    execute_session_details = genai_agent_service_bmc_python_client.models.ExecuteSessionDetails(
        user_message=str(user_input), should_stream=False  # You can set this to True for streaming responses
    )
    execute_session_response = genai_agent_runtime_client.execute_session(agent_endpoint_id, st.session_state.session_id, execute_session_details)

    # Display agent response
    if execute_session_response.status == 200:
        response_content = execute_session_response.data.message.content
        st.session_state.messages.append({"role": "assistant", "content": response_content.text})
        with st.chat_message("assistant"):
            st.markdown(response_content.text)

        if response_content.citations:
            with st.expander("Citations"):  # Collapsable section
                for citation in response_content.citations:
                    st.markdown(f"- [{citation.source_location.url}]({citation.source_location.url})")
    else:
        st.error(f"API request failed with status: {execute_session_response.status}")


# Sidebar
with st.sidebar:
    st.sidebar.title("Options")
    option = st.selectbox(
        "Select the Endpoint?",
        ("Chat-xxx3qeq","SQL-xxxocma"))
    if st.button("Reload", type="primary", use_container_width=True, help="Clear History /Update endpoint"):
        if option == "Chat-xxx3qeq":
            os.environ["oci_agent_endpoint"] = "cid1.genaiagentendpoint.oc1.us-chicago-1.amaaaaaafigrwqya27wppncqffppk4wdeertiaxt46y3dunqwox4a27x3qeq"
        elif option == "SQL-xxxocma":
            os.environ["oci_agent_endpoint"] = "ocid1.genaiagentendpoint.oc1.us-chicago-1.amaaaaaafigrwqyarfhk4nkxg2x6mizfcojh5fzgqbabserm5yjqk44rocma"
        else:
            st.error("Broken selection")
        st.session_state.messages = []
        st.session_state.session_id = None
        print(os.environ['oci_agent_endpoint'])
        st.rerun()
