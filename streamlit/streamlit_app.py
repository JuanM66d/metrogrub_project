import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit.components.v1 as components

from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="MetroGrub Analytics Dashboard",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("MetroGrub Site Selection 🍔")

# Embed URLs for each Looker Studio map
map_url_1 = "https://panderasystems.looker.com/embed/dashboards/2490"
map_url_2 = "https://panderasystems.looker.com/embed/dashboards/734"

# Create tabs
tab1, tab2 = st.tabs(["🗺️ Location Zone Map", "📍 Location Point Map"])

with tab1:
    st.subheader("Analyze Average Scores by Zone")
    components.html(
        f'<iframe src="{map_url_1}" width="100%" height="800" frameborder="0" allowfullscreen></iframe>',
        height=820,
    )

with tab2:
    st.subheader("Competitor Locations & Businesses")
    components.html(
        f'<iframe src="{map_url_2}" width="100%" height="800" frameborder="0" allowfullscreen></iframe>',
        height=820,
    )


# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit | MetroGrub Analytics Platform") 