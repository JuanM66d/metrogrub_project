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

sidebar_chat()

# Embed URLs for each Looker Studio map
map_url_1 = "https://panderasystems.looker.com/embed/dashboards/734"
map_url_2 = "https://panderasystems.looker.com/embed/dashboards/2490"

# Create tabs
tab1, tab2 = st.tabs(["📍 Location Point Map","🗺️ Location Zone Map"])

with tab1:
    st.subheader("Analyze Average Scores by Zone")
    components.html(
        f'<iframe src="{map_url_1}" width="100%" height="2000" frameborder="0" allowfullscreen></iframe>',
        height=2000,
        width=2000,
    )

with tab2:
    st.subheader("Competitor Locations & Businesses")
    components.html(
        f'<iframe src="{map_url_2}" width="100%" height="2000" frameborder="0" allowfullscreen></iframe>',
        height=2000,
        width=2000,
    )


# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit | MetroGrub Analytics Platform") 