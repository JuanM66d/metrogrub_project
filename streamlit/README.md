# MetroGrub Streamlit Dashboard

A basic Streamlit dashboard for visualizing MetroGrub analytics data including food inspections, demographics, business licenses, and foot traffic patterns.

### Local Dev Using Docker

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

2. Open your browser to `http://localhost:8501`


#### Deployment
```bash
./deploy_streamlit.sh
```
This will update gcloud run instance with updated streamlit and docker configuration

## Environment Variables

- `STREAMLIT_SERVER_PORT`: Port for the Streamlit server (default: 8501)
- `STREAMLIT_SERVER_ADDRESS`: Address to bind the server (default: 0.0.0.0)

## Health Check

The container includes a health check endpoint at `/_stcore/health` for monitoring purposes. 