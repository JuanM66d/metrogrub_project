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
    st.subheader("Analyze Average Scores by Zone")
    components.html(
        f'<iframe src="{signed_url_1}" width="100%" height="2000" frameborder="0" allowfullscreen></iframe>',
        height=1150,
        width=2000,
    )

with tab2:
    st.subheader("Competitor Locations & Businesses")
    components.html(
        f'<iframe src="{signed_url_2}" width="100%" height="2000" frameborder="0" allowfullscreen></iframe>',
        height=1150,
        width=2000,
    )

st.write(signed_url_1)
st.write("--------------------------------")
st.write("https://panderasystems.looker.com/login/embed/%2Fembed%2Fdashboards%2F734%3FCategory%3D%26Entity%2BName%3D%26Final%2BLocation%2BScore%3D%255B0%252C100%255D%26Address%3D?permissions=%5B%22access_data%22%2C%22see_looks%22%2C%22see_user_dashboards%22%5D&models=%5B%22metrogrub_data%22%5D&signature=vISMXxZp8ri2C0WLMSncAa%2FEEfs%3D&nonce=%226f5362cb95826ba8359dde962d93f7e5%22&time=1754947428&session_length=300&external_user_id=%22metrogrub_app%22&access_filters=%7B%7D&user_attributes=%7B%7D&force_logout_login=true")


# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit | MetroGrub Analytics Platform") 