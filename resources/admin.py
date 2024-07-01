import os
import time
import json
import shortuuid
import streamlit as st


class Admin:
    def __init__(self, logger):
        self.logger = logger
        self.config_file = "config/endpoints.json"
        st.subheader("Administrative actions.")

    def config_actions(self):
        self.logger.info("Running config actions")
        try:
            col1 , col2  = st.columns ([2,2])
            try:
                with col1:
                    with open(self.config_file) as file:
                        data = json.load(file)
                file_name = f"endpoint_config_{shortuuid.ShortUUID().random(length=6)}.json"
                if st.download_button("⬇Download Endpoint Config", str(data), file_name, type="primary", use_container_width=False, help="Download Endpoint Config"):
                    self.logger.info(f"Downloaded config {file_name}")
                try:
                    uploaded_file = st.file_uploader("Chose endpoint config",type=['json'],on_change=None)
                    try:
                        admin_password = os.environ['admin_password']
                        password = st.text_input("Enter administrator password" , type="password",on_change=None)
                        try:
                            if st.button("✔️ Upload Config", help="Upload endpoint config"):
                                self.file_upload_actions(uploaded_file, password, admin_password)
                        except Exception as error:
                            self.logger.error(f"File actions failed - {str(error)}")
                            self.warning_message("File action failed - contact administrator")

                    except KeyError:
                        self.warning_message("Admin actions are not enabled - contact administrator")
                        self.logger.error("Rejected admin upload as admin_password environment not found ")
                except Exception as error:
                    self.logger.error(f"Upload config failed {str(error)}")
                    print(error)
                    self.warning_message("Upload endpoint configuration failed - contact administrator")
            except Exception as error:
                self.logger.error(f"Download config failed {str(error)}")
                self.warning_message("Download endpoint configuration failed - contact administrator")
        except Exception as error:
            self.logger.error(f"Config actions failed {error}")

    def file_upload_actions(self, uploaded_file, password, admin_password):
        try:
            self.logger.info("Starting file actions")
            if uploaded_file is not None:
                data = uploaded_file.read()
                data_to_write = json.loads(data.decode().replace("'", '"'))
                self.validate_default_key(data_to_write)
                if password != admin_password:
                    self.logger.error("Invalid password- aborting upload")
                    self.warning_message("Wrong administrator password- aborting upload , Reupload or contact administrator")
                else:
                    with open(self.config_file, 'w') as config_file:
                        json.dump(data_to_write, config_file)
                    self.logger.info(f"File uploaded with data {str(data_to_write)}")
                    st.info("File Upload completed")
                    with st.spinner('Reloading to Chat page in 2s...'):
                        time.sleep(2)
                        self.logger.info("Switching to chat ui.")
                        st.switch_page("Chat.py")

        except Exception as error:
            print(error)
            self.warning_message("File upload failed - contact administrator")
            self.logger.error(f"File actions failed - {str(error)}")

    def validate_default_key(self, data_to_write):
        default_key = os.getenv('default_key',default="Chat")
        self.logger.info(f"Validating default key - {default_key}")
        try:
            endpoint_value_for_default = data_to_write[default_key]
            self.logger.info(f"Validated default key {default_key} with value {endpoint_value_for_default}")
        except KeyError:
            self.logger.error(f"Default key {default_key} not present in the uploaded file")
            self.warning_message(f"Default key '{default_key}' not present in the uploaded file - Reupload or contact administrator.")
            st.stop()

    def admin_actions(self):
        self.config_actions()

    def call_cancel(self, message):
        print(message)
        self.logger.info(f"Cancel request from user function {message}")
        st.rerun()
    def warning_message(self, message):
        self.logger.info(f"Warning message invoked - {message}")
        st.warning(message, icon="⚠️")
