# MetroGrub Streamlit Dashboard

A basic Streamlit dashboard for visualizing MetroGrub analytics data including food inspections, demographics, business licenses, and foot traffic patterns.


### SETUP for chatbot

#### Google Cloud Authentication

Before running the application, you need to set up Google Cloud authentication:

1. **Install Google Cloud CLI** (if not already installed):
   ```bash
   # macOS
   brew install google-cloud-sdk
   
   # Other platforms: https://cloud.google.com/sdk/docs/install
   ```

2. **Authenticate with Google Cloud**:
   ```bash
   gcloud auth application-default login
   ```
   This will open a browser window for authentication and save credentials to `~/.config/gcloud/application_default_credentials.json`

   **Note for Team Members**: The docker-compose.yml uses `${HOME}/.config/gcloud/application_default_credentials.json` which automatically resolves to each developer's home directory.

3. **Set up environment variables**:
   Create a `.env` file in the `streamlit/` directory with:
   ```
   LOOKER_CLIENT_ID=your_looker_client_id_here
   LOOKER_CLIENT_SECRET=your_looker_client_secret_here
   ```

For Looker API credentials setup, see: https://cloud.google.com/looker/docs/api-auth 

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