################# CLOUD FUNCTIONS STORAGE BUCKET

resource "google_storage_bucket" "metrogrub_cloud_function_bucket" {
  name     = "metrogrub-cloud-function-bucket-${var.project_id}"
  location = "US"
  force_destroy = true
}

################# MASTER TABLE

resource "google_storage_bucket_object" "master_table_function_zip" {
  name   = "master_table.zip"
  bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source = "../cloud_functions/master/master_table/master_table.zip"
}

################# DEMOGRAPHICS DATA

resource "google_storage_bucket_object" "demographics_function_zip" {
  name   = "demographics_data.zip"
  bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source = "../cloud_functions/ingestion/demographics_data/demographics_data.zip"
}

resource "google_storage_bucket_object" "clean_demographics_function_zip" {
  name   = "clean_demographics_data.zip"
  bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source = "../cloud_functions/cleaning/demographics_data/demographics_data.zip"
}

################# ZONING DATA

resource "google_storage_bucket_object" "zoning_function_zip" {
  name   = "zoning_data.zip"
  bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source = "../cloud_functions/ingestion/zoning_data/zoning_data.zip"
}

resource "google_storage_bucket_object" "clean_zoning_function_zip" {
  name   = "clean_zoning_data.zip"
  bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source = "../cloud_functions/cleaning/zoning_data/zoning_data.zip"
}

################# ACTIVE BUSINESS LICENSE DATA

resource "google_storage_bucket_object" "business_licenses_function_zip" {
  name   = "business_licenses.zip"
  bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source = "../cloud_functions/ingestion/business_license_data/business_licenses.zip"
}

resource "google_storage_bucket_object" "clean_business_licenses_function_zip" {
  name   = "clean_business_licenses.zip"
  bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source = "../cloud_functions/cleaning/business_license_data/clean_business_licenses.zip"
}

################# FOOD INSPECTION DATA

resource "google_storage_bucket_object" "food_inspections_function_zip" {
  name   = "food_inspections.zip"
  bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source = "../cloud_functions/ingestion/food_inspections_data/food_inspections.zip"
}

resource "google_storage_bucket_object" "clean_food_inspections_function_zip" {
  name   = "food_inspections.zip"
  bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source = "../cloud_functions/cleaning/food_inspections_data/food_inspections.zip"
}

################# DIVVY STATION DATA

resource "google_storage_bucket_object" "divvy_stations_function_zip" {
  name   = "divvy_stations.zip"
  bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source = "../cloud_functions/ingestion/divvy_stations_data/divvy_stations.zip"
}

resource "google_storage_bucket_object" "clean_divvy_stations_function_zip" {
  name   = "clean_divvy_stations.zip"
  bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source = "../cloud_functions/cleaning/divvy_stations/divvy_stations.zip"
}

################# CTA BUS STATION DATA

resource "google_storage_bucket_object" "cta_bus_stations_function_zip" {
  name   = "cta_bus_stations.zip"
  bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source = "../cloud_functions/ingestion/cta_bus_stations_data/cta_bus_stations.zip"
}

resource "google_storage_bucket_object" "clean_cta_bus_stations_function_zip" {
  name   = "clean_cta_bus_stations.zip"
  bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source = "../cloud_functions/cleaning/bus_stations/cta_bus_stations.zip"
}

################# FOOT TRAFFIC DATA

resource "google_storage_bucket_object" "gen_foot_traffic_function_zip" {
  name   = "gen_foot_traffic_data.zip"
  bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source = "../cloud_functions/generation/foot_traffic_data/gen_foot_traffic_data.zip"
}