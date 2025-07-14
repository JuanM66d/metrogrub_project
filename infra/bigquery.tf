################# DEMOGRAPHICS DATA

resource "google_bigquery_dataset" "demographics" {
  dataset_id = "chicago_demographics"
  location   = "US"
}

resource "google_bigquery_table" "population_counts" {
  dataset_id = google_bigquery_dataset.demographics.dataset_id
  table_id   = "population_counts"

  deletion_protection = false

  schema = file("${path.module}/schema/population_schema.json")
}

resource "google_bigquery_table" "clean_population_counts" {
  dataset_id = google_bigquery_dataset.demographics.dataset_id
  table_id   = "clean_population_counts"

  deletion_protection = false
}

################# ZONING DATA

resource "google_bigquery_dataset" "zoning" {
  dataset_id = "chicago_zoning"
  location   = "US"
}

resource "google_bigquery_table" "zoning_data" {
  dataset_id = google_bigquery_dataset.zoning.dataset_id
  table_id   = "zoning_data"

  deletion_protection = false

  schema = file("${path.module}/schema/zoning_schema.json")
}

resource "google_bigquery_table" "clean_zoning_data" {
  dataset_id = google_bigquery_dataset.zoning.dataset_id
  table_id   = "clean_zoning_data"

  deletion_protection = false
}

################# ACTIVE BUSINESS LICENSE DATA

resource "google_bigquery_dataset" "business_licenses" {
  dataset_id = "chicago_active_business_licenses"
  location   = "US"
}

resource "google_bigquery_table" "active_business_licenses" {
  dataset_id = google_bigquery_dataset.business_licenses.dataset_id
  table_id   = "active_business_licenses"

  deletion_protection = false

  schema = file("${path.module}/schema/active_business_licenses_schema.json")
}

resource "google_bigquery_table" "clean_active_business_licenses" {
  dataset_id = google_bigquery_dataset.business_licenses.dataset_id
  table_id   = "clean_active_business_licenses"

  deletion_protection = false
}

################# FOOD INSPECTION DATA

resource "google_bigquery_dataset" "food_inspections" {
  dataset_id = "chicago_food_inspections"
  location   = "US"
}

resource "google_bigquery_table" "food_inspections" {
  dataset_id = google_bigquery_dataset.food_inspections.dataset_id
  table_id   = "food_inspections_data"

  deletion_protection = false

  schema = file("${path.module}/schema/food_inspections_schema.json")
}

resource "google_bigquery_table" "clean_food_inspections" {
  dataset_id = google_bigquery_dataset.food_inspections.dataset_id
  table_id   = "clean_food_inspections_data"

  deletion_protection = false
}


################# DIVVY STATION DATA

resource "google_bigquery_dataset" "divvy_stations" {
  dataset_id = "divvy_stations"
  location   = "US"
}

resource "google_bigquery_table" "divvy_stations" {
  dataset_id = google_bigquery_dataset.divvy_stations.dataset_id
  table_id   = "divvy_stations_data"

  deletion_protection = false

  schema = file("${path.module}/schema/divvy_stations_schema.json")
}

resource "google_bigquery_table" "clean_divvy_stations" {
  dataset_id = google_bigquery_dataset.divvy_stations.dataset_id
  table_id   = "clean_divvy_stations_data"

  deletion_protection = false
}

################# CTA BUS DATA

resource "google_bigquery_dataset" "cta_bus_stations" {
  dataset_id = "cta_bus_stations"
  location   = "US"
}

resource "google_bigquery_table" "cta_bus_stations" {
  dataset_id = google_bigquery_dataset.cta_bus_stations.dataset_id
  table_id   = "cta_bus_stations_data"

  deletion_protection = false

  schema = file("${path.module}/schema/cta_bus_stations_schema.json")
}

resource "google_bigquery_table" "clean_cta_bus_stations" {
  dataset_id = google_bigquery_dataset.cta_bus_stations.dataset_id
  table_id   = "clean_cta_bus_stations"

  deletion_protection = false
}