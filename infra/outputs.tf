# # Cloud Run service URL
# output "streamlit_app_url" {
#   description = "URL of the deployed Streamlit application"
#   value       = google_cloud_run_v2_service.streamlit_service.uri
# }

# Artifact Registry repository details
output "artifact_registry_repository" {
  description = "Artifact Registry repository for the Streamlit app"
  value       = google_artifact_registry_repository.streamlit_repo.name
}

# Docker image push command
output "docker_push_command" {
  description = "Command to push Docker image to Artifact Registry"
  value       = "docker tag streamlit-app:latest ${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.streamlit_repo.repository_id}/streamlit-app:latest && docker push ${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.streamlit_repo.repository_id}/streamlit-app:latest"
}
