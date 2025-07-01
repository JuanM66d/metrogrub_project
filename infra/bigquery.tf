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