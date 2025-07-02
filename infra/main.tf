provider "google" {
  project = var.project_id
  region  = var.region
}

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    bucket = "tf-state-bucket-pmetrogrub"
    prefix  = "terraform/state"
  }

  required_version = ">= 1.5.0"
}
