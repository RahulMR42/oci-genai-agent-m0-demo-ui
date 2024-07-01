### A UI for OCI Generative AI Agent .

#### Features
- Basic access control.
- Ability to work across regions.
- Ability to add endpoint/s as favorite for frequent usages.
- Ability to run against agent endpoints.
- Ability to add feedback and download summary.
- Logging and tracing.
- Administrative control.

#### How to use 

- Clone the repo 
```shell
git clone https://github.com/RahulMR42/oci-genai-agent-m0-demo-ui
```
- Install requirements

```shell
virtualenv env
source env/bin/activate
pip install streamlit oci streamlit_feedback
pip install genai_agent_service_bmc_python_client-<>-py2.py3-none-any.whl #As its a beta service refer Oracle rep or engineering team note and use the appropriate version
```
- Set credentials for users
```shell
vi .streamlit/secrets.toml #Refer the format and update credentials 
```
- Add Agent endpoint OCID/OCIDs ,we need atleast one active endpoint
```shell
vi config/endpoints.json
```
- Its a simple Json format, Add at least one endpoint with a humane readable name 
```shell
{
  "Chat":"Agent-Ocid1",
  "AnotherOne":"Agent-Ocid2"
}
```
- When using the `ChatUI` ,It will display these endpoints humane readable name for user to select. By default, it expects an endpoint with name as Chat, if you wish to use another name, you may set below environment variable.
- Forbidden to use "Custom" as a endpoint key

```shell
export default_key = "AnotherDefaultKey"
```
- Set an administrator password (A stronger and complex one), this is not for users but for admins to run Administrative actions via UI, Its optional to allow administrative `edit/update` actions via UI.
```shell
export admin_password="<A Complicated one >"
```
- Run the app 
```shell
streamlit run Chat.py 
```







