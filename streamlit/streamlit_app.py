import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="MetroGrub Analytics Dashboard",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main title
st.title("🍔 MetroGrub Analytics Dashboard")
st.markdown("Welcome to the MetroGrub data analytics platform!")

# Sidebar
st.sidebar.header("Dashboard Controls")
selected_metric = st.sidebar.selectbox(
    "Select Metric",
    ["Food Inspections", "Demographics", "Business Licenses", "Foot Traffic"]
)

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(datetime.now() - timedelta(days=30), datetime.now()),
    format="YYYY-MM-DD"
)

# Main content area
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Total Restaurants",
        value="1,234",
        delta="12"
    )

with col2:
    st.metric(
        label="Food Inspections",
        value="5,678",
        delta="-23"
    )

with col3:
    st.metric(
        label="Average Rating",
        value="4.2",
        delta="0.1"
    )

# Sample data visualization
st.subheader(f"📊 {selected_metric} Analysis")

if selected_metric == "Food Inspections":
    # Generate sample data
    # Handle both single date and date range
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range[0], date_range[1]
    else:
        # If single date selected, use it as both start and end
        start_date = end_date = date_range
    
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    inspection_data = pd.DataFrame({
        'Date': dates,
        'Inspections': np.random.randint(10, 50, len(dates)),
        'Violations': np.random.randint(0, 20, len(dates))
    })
    
    fig = px.line(inspection_data, x='Date', y=['Inspections', 'Violations'],
                  title="Daily Food Inspections and Violations")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Recent Inspections")
    st.dataframe(inspection_data.tail(10), use_container_width=True)

elif selected_metric == "Demographics":
    # Sample demographic chart
    demo_data = pd.DataFrame({
        'Age Group': ['18-25', '26-35', '36-45', '46-55', '55+'],
        'Population': [12000, 18500, 15200, 11800, 9300]
    })
    
    fig = px.bar(demo_data, x='Age Group', y='Population',
                 title="Population by Age Group")
    st.plotly_chart(fig, use_container_width=True)

elif selected_metric == "Business Licenses":
    # Sample business license data
    license_data = pd.DataFrame({
        'License Type': ['Restaurant', 'Food Truck', 'Catering', 'Bar/Tavern', 'Coffee Shop'],
        'Count': [450, 123, 87, 234, 189]
    })
    
    fig = px.pie(license_data, values='Count', names='License Type',
                 title="Business License Distribution")
    st.plotly_chart(fig, use_container_width=True)

else:  # Foot Traffic
    # Sample foot traffic data
    hours = list(range(6, 23))
    traffic_data = pd.DataFrame({
        'Hour': hours,
        'Foot Traffic': [50, 75, 120, 180, 220, 280, 350, 420, 450, 380, 320, 280, 240, 200, 180, 160, 140]
    })
    
    fig = px.area(traffic_data, x='Hour', y='Foot Traffic',
                  title="Daily Foot Traffic Pattern")
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit | MetroGrub Analytics Platform") 