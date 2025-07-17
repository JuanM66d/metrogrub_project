# Artifact Registry repository for storing Docker images
resource "google_artifact_registry_repository" "streamlit_repo" {
  location      = var.region
  repository_id = "streamlit-app"
  description   = "Repository for MetroGrub Streamlit application images"
  format        = "DOCKER"

  cleanup_policies {
    id     = "keep-minimum-versions"
    action = "KEEP"
    most_recent_versions {
      keep_count = 5
    }
  }
}

# Service account for Cloud Run
resource "google_service_account" "streamlit_service_account" {
  account_id   = "streamlit-app-sa"
  display_name = "Streamlit App Service Account"
  description  = "Service account for the MetroGrub Streamlit application"
}

# IAM permissions for the service account to read BigQuery data
resource "google_project_iam_member" "streamlit_bigquery_data_viewer" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.streamlit_service_account.email}"
}

resource "google_project_iam_member" "streamlit_bigquery_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.streamlit_service_account.email}"
}

# Cloud Run service
# resource "google_cloud_run_v2_service" "streamlit_service" {
#   name     = "metrogrub-streamlit-app"
#   location = var.region
#   ingress  = "INGRESS_TRAFFIC_ALL"

#   template {
#     service_account = google_service_account.streamlit_service_account.email
    
#     containers {
#       image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.streamlit_repo.repository_id}/streamlit-app:latest"
      
#       ports {
#         container_port = 8501
#       }

#       env {
#         name  = "STREAMLIT_SERVER_PORT"
#         value = "8501"
#       }

#       env {
#         name  = "STREAMLIT_SERVER_ADDRESS"
#         value = "0.0.0.0"
#       }

#       env {
#         name  = "GOOGLE_CLOUD_PROJECT"
#         value = var.project_id
#       }

#       resources {
#         limits = {
#           cpu    = "1"
#           memory = "1Gi"
#         }
#         cpu_idle = true
#       }

#       startup_probe {
#         http_get {
#           path = "/_stcore/health"
#           port = 8501
#         }
#         initial_delay_seconds = 10
#         timeout_seconds       = 5
#         period_seconds        = 10
#         failure_threshold     = 3
#       }

#       liveness_probe {
#         http_get {
#           path = "/_stcore/health"
#           port = 8501
#         }
#         initial_delay_seconds = 30
#         timeout_seconds       = 5
#         period_seconds        = 30
#         failure_threshold     = 3
#       }
#     }

#     scaling {
#       min_instance_count = 0
#       max_instance_count = 10
#     }

#     timeout = "300s"
#   }

#   traffic {
#     type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
#     percent = 100
#   }

#   depends_on = [
#     google_artifact_registry_repository.streamlit_repo
#   ]
# }

# # IAM policy to allow unauthenticated access to Cloud Run service
# resource "google_cloud_run_service_iam_member" "streamlit_public_access" {
#   location = google_cloud_run_v2_service.streamlit_service.location
#   service  = google_cloud_run_v2_service.streamlit_service.name
#   role     = "roles/run.invoker"
#   member   = "allUsers"
# }

# IAM permissions for Artifact Registry
resource "google_artifact_registry_repository_iam_member" "streamlit_repo_reader" {
  project    = var.project_id
  location   = google_artifact_registry_repository.streamlit_repo.location
  repository = google_artifact_registry_repository.streamlit_repo.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.streamlit_service_account.email}"
} 