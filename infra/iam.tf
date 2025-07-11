################# SCHEDULER INVOKER SERVICE ACCOUNT

resource "google_service_account" "scheduler_invoker" {
  account_id   = "scheduler-invoker"
  display_name = "Cloud Scheduler Invoker Service Account"
}

################# DEMOGRAPHICS DATA

resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = google_cloudfunctions_function.demographics_function.project
  region         = google_cloudfunctions_function.demographics_function.region
  cloud_function = google_cloudfunctions_function.demographics_function.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}

resource "google_cloudfunctions_function_iam_member" "scheduler_invoker" {
  project        = google_cloudfunctions_function.demographics_function.project
  region         = google_cloudfunctions_function.demographics_function.region
  cloud_function = google_cloudfunctions_function.demographics_function.name

  role   = "roles/cloudfunctions.invoker"
  member = "serviceAccount:${google_service_account.scheduler_invoker.email}"
}

################# ZONING DATA

resource "google_cloudfunctions_function_iam_member" "zoning_invoker" {
  project        = google_cloudfunctions_function.zoning_function.project
  region         = google_cloudfunctions_function.zoning_function.region
  cloud_function = google_cloudfunctions_function.zoning_function.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}

################# ACTIVE BUSINESS LICENSE DATA

resource "google_cloudfunctions_function_iam_member" "business_licenses_invoker" {
  project        = google_cloudfunctions_function.business_licenses_function.project
  region         = google_cloudfunctions_function.business_licenses_function.region
  cloud_function = google_cloudfunctions_function.business_licenses_function.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}

resource "google_cloudfunctions_function_iam_member" "clean_business_licenses_invoker" {
  project        = google_cloudfunctions_function.clean_business_licenses_function.project
  region         = google_cloudfunctions_function.clean_business_licenses_function.region
  cloud_function = google_cloudfunctions_function.clean_business_licenses_function.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}

################# FOOD INSPECTION DATA

resource "google_cloudfunctions_function_iam_member" "food_inspections_invoker" {
  project        = google_cloudfunctions_function.food_inspections_function.project
  region         = google_cloudfunctions_function.food_inspections_function.region
  cloud_function = google_cloudfunctions_function.food_inspections_function.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}

################# DIVVY STATION DATA

resource "google_cloudfunctions_function_iam_member" "divvy_stations_invoker" {
  project        = google_cloudfunctions_function.divvy_stations_function.project
  region         = google_cloudfunctions_function.divvy_stations_function.region
  cloud_function = google_cloudfunctions_function.divvy_stations_function.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}

################# BUS STATION STATION DATA

resource "google_cloudfunctions_function_iam_member" "cta_bus_stations_invoker" {
  project        = google_cloudfunctions_function.cta_bus_stations_function.project
  region         = google_cloudfunctions_function.cta_bus_stations_function.region
  cloud_function = google_cloudfunctions_function.cta_bus_stations_function.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}