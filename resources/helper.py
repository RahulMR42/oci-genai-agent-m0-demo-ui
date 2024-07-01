import time
import streamlit as st

def help_images():
    st.subheader("Help videos")
    my_expander1 = st.expander("How to Use Chat UI ", expanded=True)
    with my_expander1:
        st.image("help_images/ChatUI.gif")
    my_expander2 = st.expander("How to use use sidebar ", expanded=False)
    with my_expander2:
        st.image("help_images/SideBar.gif")
    my_expander3 = st.expander("How to use Administrative functions", expanded=False)
    with my_expander3:
        st.image("help_images/AdminAction.gif")
