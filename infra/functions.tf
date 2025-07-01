################# DEMOGRAPHICS DATA 
resource "google_cloudfunctions_function" "demographics_function" {
  name        = "ingest-chicago-demographics"
  runtime     = "python310"
  entry_point = "ingest_chicago_demographics"

  source_archive_bucket = google_storage_bucket.demographics_data_function_bucket.name
  source_archive_object = google_storage_bucket_object.demographics_function_zip.name

  trigger_http = true

  available_memory_mb = 256

  environment_variables = {
    "BIGQUERY_TABLE" = "${google_bigquery_table.population_counts.id}"
  }
}


################# ZONING DATA

resource "google_cloudfunctions_function" "zoning_function" {
  name        = "ingest-chicago-zoning"
  runtime     = "python310"
  entry_point = "ingest_chicago_zoning"

  source_archive_bucket = google_storage_bucket.demographics_data_function_bucket.name
  source_archive_object = google_storage_bucket_object.zoning_function_zip.name

  trigger_http = true
  available_memory_mb = 256

  environment_variables = {
    "BIGQUERY_TABLE" = google_bigquery_table.zoning_data.id
  }
}

################# ACTIVE BUSINESS LICENSE DATA

resource "google_cloudfunctions_function" "business_licenses_function" {
  name        = "ingest-chicago-business-licenses"
  runtime     = "python310"
  entry_point = "ingest_chicago_business_licenses"

  source_archive_bucket = google_storage_bucket.demographics_data_function_bucket.name
  source_archive_object = google_storage_bucket_object.business_licenses_function_zip.name

  trigger_http = true
  available_memory_mb = 256

  environment_variables = {
    "BIGQUERY_TABLE" = google_bigquery_table.active_business_licenses.id
  }
}

################# FOOD INSPECTION DATA

resource "google_cloudfunctions_function" "food_inspections_function" {
  name        = "ingest-chicago-food-inspections"
  runtime     = "python310"
  entry_point = "ingest_chicago_food_inspections"

  source_archive_bucket = google_storage_bucket.demographics_data_function_bucket.name
  source_archive_object = google_storage_bucket_object.food_inspections_function_zip.name

  trigger_http = true
  available_memory_mb = 256

  environment_variables = {
    "BIGQUERY_TABLE" = google_bigquery_table.food_inspections.id
  }
}