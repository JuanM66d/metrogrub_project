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
st.divider()

components.iframe("https://panderasystems.looker.com/embed/dashboards/734", height=1000)

# components.iframe("https://panderasystems.looker.com/datascope/ab56065b-5a38-42b0-93a1-a1e49b7e072f", height=1000)


# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit | MetroGrub Analytics Platform") 