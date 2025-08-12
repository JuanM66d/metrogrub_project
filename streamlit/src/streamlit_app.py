from pandas.core.ops.docstrings import key
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit.components.v1 as components
import sys
import os
from sidebar_chatbot import sidebar_chat
from create_signed_embed_url import get_signed_url

# Add the chatbot directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'chatbot'))

# Page configuration
st.set_page_config(
    page_title="MetroGrub Analytics Dashboard",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 5rem;
        padding-left: 4rem;
        padding-right: 5rem;
    }

    [data-testid="stSidebar"][aria-expanded="true"] {
        min-width: 350px !important;
    }
</style>
""", unsafe_allow_html=True)

# Main content
st.title("MetroGrub Site Selection 🍔")


with st.sidebar:
    sidebar_chat()


signed_url_1 = get_signed_url("734")
signed_url_2 = get_signed_url("2490")
     

# Create tabs
tab1, tab2 = st.tabs(["📍 Location Point Map","🗺️ Location Zone Map"])

with tab1:
    st.subheader("Competitor Locations & Businesses")
    components.html(
        f'<iframe src="{signed_url_1}" width="100%" height="2000" frameborder="0" allowfullscreen></iframe>',
        height=1150,
        width=2000,
    )

with tab2:
    st.subheader("Analyze Average Scores by Zone")
    components.html(
        f'<iframe src="{signed_url_2}" width="100%" height="2000" frameborder="0" allowfullscreen></iframe>',
        height=1150,
        width=2000,
    )

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit | MetroGrub Analytics Platform") 