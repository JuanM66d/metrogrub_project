################# DEMOGRAPHICS DATA

resource "google_storage_bucket" "demographics_data_function_bucket" {
  name     = "demographics-data-function-bucket-${var.project_id}"
  location = "US"
}

resource "google_storage_bucket_object" "demographics_function_zip" {
  name   = "demographics_data.zip"
  bucket = google_storage_bucket.demographics_data_function_bucket.name
  source = "../cloud_functions/demographics_data/demographics_data.zip"
}

################# ZONING DATA

resource "google_storage_bucket_object" "zoning_function_zip" {
  name   = "zoning_data.zip"
  bucket = google_storage_bucket.demographics_data_function_bucket.name
  source = "../cloud_functions/zoning_data/zoning_data.zip"
}

################# ACTIVE BUSINESS LICENSE DATA

resource "google_storage_bucket_object" "business_licenses_function_zip" {
  name   = "business_licenses.zip"
  bucket = google_storage_bucket.demographics_data_function_bucket.name
  source = "../cloud_functions/business_license_data/business_licenses.zip"
}

################# FOOD INSPECTION DATA

resource "google_storage_bucket_object" "food_inspections_function_zip" {
  name   = "food_inspections.zip"
  bucket = google_storage_bucket.demographics_data_function_bucket.name
  source = "../cloud_functions/food_inspections_data/food_inspections.zip"
}