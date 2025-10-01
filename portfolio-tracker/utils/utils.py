import streamlit  as st
import time
import os

class ExitButton:
    @staticmethod
    def exit_button():
        """ Method to exit the app via button for all streamlit pages """
        if st.button("Exit", key="exit_button_1", type="primary"):
            st.toast("Logout!", icon="🌴")
            time.sleep(0.5)
            os._exit(0)
