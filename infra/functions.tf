################# MASTER TABLE

resource "google_cloudfunctions_function" "master_table_function" {
  name        = "create-master-table"
  runtime     = "python310"
  entry_point = "create_master_table"

  source_archive_bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source_archive_object = google_storage_bucket_object.master_table_function_zip.name

  trigger_http = true

  available_memory_mb = 1024

  environment_variables = {
    FOOD_INSPECTIONS_TABLE     = "${google_bigquery_table.clean_food_inspections.project}.${google_bigquery_table.clean_food_inspections.dataset_id}.${google_bigquery_table.clean_food_inspections.table_id}"

    FOOD_LICENSES_TABLE        = "${google_bigquery_table.clean_active_business_licenses.project}.${google_bigquery_table.clean_active_business_licenses.dataset_id}.${google_bigquery_table.clean_active_business_licenses.table_id}"

    DIVVY_STATIONS_TABLE       = "${google_bigquery_table.clean_divvy_stations.project}.${google_bigquery_table.clean_divvy_stations.dataset_id}.${google_bigquery_table.clean_divvy_stations.table_id}"

    POPULATION_COUNTS_TABLE    = "${google_bigquery_table.clean_population_counts.project}.${google_bigquery_table.clean_population_counts.dataset_id}.${google_bigquery_table.clean_population_counts.table_id}"

    ZONING_DATA_TABLE          = "${google_bigquery_table.clean_zoning_data.project}.${google_bigquery_table.clean_zoning_data.dataset_id}.${google_bigquery_table.clean_zoning_data.table_id}"

    BUS_STATIONS_TABLE         = "${google_bigquery_table.clean_cta_bus_stations.project}.${google_bigquery_table.clean_cta_bus_stations.dataset_id}.${google_bigquery_table.clean_cta_bus_stations.table_id}"

    FOOT_TRAFFIC_TABLE         = var.foot_traffic_table

    OUTPUT_TABLE               = "${google_bigquery_table.master_table_final.project}.${google_bigquery_table.master_table_final.dataset_id}.${google_bigquery_table.master_table_final.table_id}"

    ZIP_BUCKET = google_storage_bucket.metrogrub_cloud_function_bucket.name
    ZIP_PREFIX = "zip_shapes/"
  }
}

################# DEMOGRAPHICS DATA 

resource "google_cloudfunctions_function" "demographics_function" {
  name        = "ingest-chicago-demographics"
  runtime     = "python310"
  entry_point = "ingest_chicago_demographics"

  source_archive_bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source_archive_object = google_storage_bucket_object.demographics_function_zip.name

  trigger_http = true

  available_memory_mb = 256

  environment_variables = {
    "BIGQUERY_TABLE" = "${google_bigquery_table.population_counts.id}"
  }
}

resource "google_cloudfunctions_function" "clean_demographics_function" {
  name        = "clean-chicago-demographics"
  runtime     = "python310"
  entry_point = "clean_chicago_demographics"

  source_archive_bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source_archive_object = google_storage_bucket_object.clean_demographics_function_zip.name

  trigger_http = true

  available_memory_mb = 256

  environment_variables = {
    "INPUT_TABLE" = "${google_bigquery_table.population_counts.project}.${google_bigquery_table.population_counts.dataset_id}.${google_bigquery_table.population_counts.table_id}"
    "OUTPUT_TABLE" = "${google_bigquery_table.clean_population_counts.project}.${google_bigquery_table.clean_population_counts.dataset_id}.${google_bigquery_table.clean_population_counts.table_id}"
  }
}


################# ZONING DATA

resource "google_cloudfunctions_function" "zoning_function" {
  name        = "ingest-chicago-zoning"
  runtime     = "python310"
  entry_point = "ingest_chicago_zoning"

  source_archive_bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source_archive_object = google_storage_bucket_object.zoning_function_zip.name

  trigger_http = true
  available_memory_mb = 512

  environment_variables = {
    "BIGQUERY_TABLE" = google_bigquery_table.zoning_data.id
  }
}

resource "google_cloudfunctions_function" "clean_zoning_function" {
  name        = "clean-chicago-zoning"
  runtime     = "python310"
  entry_point = "clean_chicago_zoning"

  source_archive_bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source_archive_object = google_storage_bucket_object.clean_zoning_function_zip.name

  trigger_http = true
  available_memory_mb = 512

  environment_variables = {
    "INPUT_TABLE" = "${google_bigquery_table.zoning_data.project}.${google_bigquery_table.zoning_data.dataset_id}.${google_bigquery_table.zoning_data.table_id}"
    "OUTPUT_TABLE" = "${google_bigquery_table.clean_zoning_data.project}.${google_bigquery_table.clean_zoning_data.dataset_id}.${google_bigquery_table.clean_zoning_data.table_id}"
  }
}

################# ACTIVE BUSINESS LICENSE DATA

resource "google_cloudfunctions_function" "business_licenses_function" {
  name        = "ingest-chicago-business-licenses"
  runtime     = "python310"
  entry_point = "ingest_chicago_business_licenses"

  source_archive_bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source_archive_object = google_storage_bucket_object.business_licenses_function_zip.name

  trigger_http = true
  available_memory_mb = 1024

  environment_variables = {
    "BIGQUERY_TABLE" = google_bigquery_table.active_business_licenses.id
  }
}

resource "google_cloudfunctions_function" "clean_business_licenses_function" {
  name        = "clean-chicago-business-licenses"
  runtime     = "python310"
  entry_point = "clean_chicago_business_licenses"

  source_archive_bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source_archive_object = google_storage_bucket_object.clean_business_licenses_function_zip.name

  trigger_http = true
  available_memory_mb = 1024

  environment_variables = {
    "INPUT_TABLE" = "${google_bigquery_table.active_business_licenses.project}.${google_bigquery_table.active_business_licenses.dataset_id}.${google_bigquery_table.active_business_licenses.table_id}"
    "OUTPUT_TABLE" = "${google_bigquery_table.clean_active_business_licenses.project}.${google_bigquery_table.clean_active_business_licenses.dataset_id}.${google_bigquery_table.clean_active_business_licenses.table_id}"
  }
}

################# FOOD INSPECTION DATA

resource "google_cloudfunctions_function" "food_inspections_function" {
  name        = "ingest-chicago-food-inspections"
  runtime     = "python310"
  entry_point = "ingest_chicago_food_inspections"

  source_archive_bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source_archive_object = google_storage_bucket_object.food_inspections_function_zip.name

  trigger_http = true
  available_memory_mb = 1024
  timeout = 540 # 9 minutes

  environment_variables = {
    "BIGQUERY_TABLE" = google_bigquery_table.food_inspections.id
  }
}

resource "google_cloudfunctions_function" "clean_food_inspections_function" {
  name        = "clean-chicago-food-inspections"
  runtime     = "python310"
  entry_point = "clean_chicago_food_inspections"

  source_archive_bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source_archive_object = google_storage_bucket_object.clean_food_inspections_function_zip.name

  trigger_http = true
  available_memory_mb = 1024
  timeout = 540 # 9 minutes

  environment_variables = {
    "INPUT_TABLE" = "${google_bigquery_table.food_inspections.project}.${google_bigquery_table.food_inspections.dataset_id}.${google_bigquery_table.food_inspections.table_id}"
    "OUTPUT_TABLE" = "${google_bigquery_table.clean_food_inspections.project}.${google_bigquery_table.clean_food_inspections.dataset_id}.${google_bigquery_table.clean_food_inspections.table_id}"
  }
}

################# DIVVY STATION DATA

resource "google_cloudfunctions_function" "divvy_stations_function" {
  name        = "ingest-divvy-station-data"
  runtime     = "python310"
  entry_point = "ingest_divvy_station_data"

  source_archive_bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source_archive_object = google_storage_bucket_object.divvy_stations_function_zip.name

  trigger_http = true
  available_memory_mb = 256

  environment_variables = {
    "BIGQUERY_TABLE" = google_bigquery_table.divvy_stations.id
  }
}

resource "google_cloudfunctions_function" "clean_divvy_stations_function" {
  name        = "clean-divvy-station-data"
  runtime     = "python310"
  entry_point = "clean_divvy_station_data"

  source_archive_bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source_archive_object = google_storage_bucket_object.clean_divvy_stations_function_zip.name

  trigger_http = true
  available_memory_mb = 256

  environment_variables = {
    "INPUT_TABLE" = "${google_bigquery_table.divvy_stations.project}.${google_bigquery_table.divvy_stations.dataset_id}.${google_bigquery_table.divvy_stations.table_id}"
    "OUTPUT_TABLE" = "${google_bigquery_table.clean_divvy_stations.project}.${google_bigquery_table.clean_divvy_stations.dataset_id}.${google_bigquery_table.clean_divvy_stations.table_id}"
  }
}

################# CTA BUS STATION DATA

resource "google_cloudfunctions_function" "cta_bus_stations_function" {
  name        = "ingest-cta-bus-station-data"
  runtime     = "python310"
  entry_point = "ingest_cta_bus_station_data"

  source_archive_bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source_archive_object = google_storage_bucket_object.cta_bus_stations_function_zip.name

  trigger_http = true
  available_memory_mb = 256

  environment_variables = {
    "BIGQUERY_TABLE" = google_bigquery_table.cta_bus_stations.id
  }
}

resource "google_cloudfunctions_function" "clean_cta_bus_stations_function" {
  name        = "clean-cta-bus-stations"
  runtime     = "python310"
  entry_point = "clean_cta_bus_stations"

  source_archive_bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source_archive_object = google_storage_bucket_object.clean_cta_bus_stations_function_zip.name

  trigger_http = true
  available_memory_mb = 1024

  environment_variables = {
    "INPUT_TABLE" = "${google_bigquery_table.cta_bus_stations.project}.${google_bigquery_table.cta_bus_stations.dataset_id}.${google_bigquery_table.cta_bus_stations.table_id}"
    "OUTPUT_TABLE" = "${google_bigquery_table.clean_cta_bus_stations.project}.${google_bigquery_table.clean_cta_bus_stations.dataset_id}.${google_bigquery_table.clean_cta_bus_stations.table_id}"
  }
}

################# FOOT TRAFFIC DATA

resource "google_cloudfunctions_function" "foot_traffic_function" {
  name        = "gen-foot-traffic-data"
  runtime     = "python310"
  entry_point = "main"

  source_archive_bucket = google_storage_bucket.metrogrub_cloud_function_bucket.name
  source_archive_object = google_storage_bucket_object.gen_foot_traffic_function_zip.name

  trigger_http = true
  available_memory_mb = 1024

}