variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud region"
  type        = string
  default     = "us-central1"
}

variable "foot_traffic_table" {
  description = "Fully-qualified BigQuery table ID (project.dataset.table)"
  type        = string
}
