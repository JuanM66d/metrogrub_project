from pandas.core.ops.docstrings import key
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit.components.v1 as components
import sys
import os
from sidebar_chatbot import sidebar_chat


# Add the chatbot directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'chatbot'))

# Page configuration
st.set_page_config(
    page_title="MetroGrub Analytics Dashboard",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main content
st.title("MetroGrub Site Selection 🍔")
st.divider()

sidebar_chat()

components.iframe("https://panderasystems.looker.com/embed/dashboards/734", height=1000)


# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit | MetroGrub Analytics Platform") 