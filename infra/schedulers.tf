################# DEMOGRAPHICS DATA SCHEDULER

resource "google_cloud_scheduler_job" "demographics_job" {
    name             = "ingest-chicago-demographics-job"
    description      = "Triggers the ingest-chicago-demographics function every 3 months"
    schedule         = "0 3 1 1,4,7,10 *" # minute 0, 3AM, on the first day, of Jan, Apr, Jul, Oct (every 3 months)
    time_zone        = "America/Chicago"

    http_target {
        http_method = "POST"
        uri         = google_cloudfunctions_function.demographics_function.https_trigger_url

        oidc_token {
        service_account_email = google_service_account.scheduler_invoker.email
        }
    }
}

resource "google_cloud_scheduler_job" "clean_demographics_job" {
    name             = "clean-chicago-demographics-job"
    description      = "Triggers the clean-chicago-demographics function every 3 months"
    schedule         = "15 3 1 1,4,7,10 *" # minute 15, 3AM, on the first day, of Jan, Apr, Jul, Oct (every 3 months)
    time_zone        = "America/Chicago"

    http_target {
        http_method = "POST"
        uri         = google_cloudfunctions_function.clean_demographics_function.https_trigger_url

        oidc_token {
        service_account_email = google_service_account.scheduler_invoker.email
        }
    }
}

################# FOOT TRAFFIC DATA SCHEDULER

resource "google_cloud_scheduler_job" "foot_traffic_job" {
    name             = "ingest-chicago-foot-traffic"
    description      = "Triggers the gen_foot_traffic_data function every 3 months"
    schedule         = "0 3 1 1,4,7,10 *" # minute 0, 3AM, on the first day, of Jan, Apr, Jul, Oct (every 3 months)
    time_zone        = "America/Chicago"

    http_target {
        http_method = "POST"
        uri         = google_cloudfunctions_function.foot_traffic_function.https_trigger_url

        oidc_token {
        service_account_email = google_service_account.scheduler_invoker.email
        }
    }
}

################# ZONING DATA SCHEDULER

resource "google_cloud_scheduler_job" "zoning_job" {
    name             = "ingest-chicago-zoning-job"
    description      = "Triggers the ingest-chicago-zoning function every 3 months"
    schedule         = "0 3 1 1,4,7,10 *" # minute 0, 3AM, on the first day, of Jan, Apr, Jul, Oct (every 3 months)
    time_zone        = "America/Chicago"

    http_target {
        http_method = "POST"
        uri         = google_cloudfunctions_function.zoning_function.https_trigger_url

        oidc_token {
        service_account_email = google_service_account.scheduler_invoker.email
        }
    }
}


################# BUSINESS LICENSES DATA SCHEDULER

resource "google_cloud_scheduler_job" "business_licenses_job" {
    name             = "ingest-chicago-business-licenses-job"
    description      = "Triggers the ingest-chicago-business-licenses function every 3 months"
    schedule         = "0 3 1 1,4,7,10 *" # minute 0, 3AM, on the first day, of Jan, Apr, Jul, Oct (every 3 months)
    time_zone        = "America/Chicago"

    http_target {
        http_method = "POST"
        uri         = google_cloudfunctions_function.business_licenses_function.https_trigger_url

        oidc_token {
        service_account_email = google_service_account.scheduler_invoker.email
        }
    }
}

resource "google_cloud_scheduler_job" "clean_business_licenses_job" {
    name             = "clean-chicago-business-licenses-job"
    description      = "Triggers the clean-chicago-business-licenses function every 3 months"
    schedule         = "15 3 1 1,4,7,10 *" # minute 15, 3AM, on the first day, of Jan, Apr, Jul, Oct (every 3 months)
    time_zone        = "America/Chicago"

    http_target {
        http_method = "POST"
        uri         = google_cloudfunctions_function.clean_business_licenses_function.https_trigger_url

        oidc_token {
        service_account_email = google_service_account.scheduler_invoker.email
        }
    }
}


################# FOOD INSPECTIONS DATA SCHEDULER

resource "google_cloud_scheduler_job" "food_inspections_job" {
    name             = "ingest-chicago-food-inspections-job"
    description      = "Triggers the ingest-chicago-food-inspections function every 3 months"
    schedule         = "0 3 1 1,4,7,10 *" # minute 0, 3AM, on the first day, of Jan, Apr, Jul, Oct (every 3 months)
    time_zone        = "America/Chicago"
    attempt_deadline = "1200s" # 20 minutes

    retry_config {
        retry_count = 3
        min_backoff_duration = "900s" # 15 minutes
        max_backoff_duration = "7200s" # 2 hours
    }

    http_target {
        http_method = "POST"
        uri         = google_cloudfunctions_function.food_inspections_function.https_trigger_url

        oidc_token {
        service_account_email = google_service_account.scheduler_invoker.email
        }
    }
}


################# DIVVY STATION DATA SCHEDULER

resource "google_cloud_scheduler_job" "divvy_stations_job" {
    name             = "ingest-chicago-divvy-stations-job"
    description      = "Triggers the ingest-chicago-divvy-stations function every 3 months"
    schedule         = "0 3 1 1,4,7,10 *" # minute 0, 3AM, on the first day, of Jan, Apr, Jul, Oct (every 3 months)
    time_zone        = "America/Chicago"

    http_target {
        http_method = "POST"
        uri         = google_cloudfunctions_function.divvy_stations_function.https_trigger_url

        oidc_token {
        service_account_email = google_service_account.scheduler_invoker.email
        }
    }
}       

################# CTA BUS STATION DATA SCHEDULER

resource "google_cloud_scheduler_job" "cta_bus_stations_job" {
    name             = "ingest-chicago-cta-bus-stations-job"
    description      = "Triggers the ingest-chicago-cta-bus-stations function every 3 months"
    schedule         = "0 3 1 1,4,7,10 *" # minute 0, 3AM, on the first day, of Jan, Apr, Jul, Oct (every 3 months)
    time_zone        = "America/Chicago"
    

    http_target {
        http_method = "POST"
        uri         = google_cloudfunctions_function.cta_bus_stations_function.https_trigger_url

        oidc_token {
        service_account_email = google_service_account.scheduler_invoker.email
        }
    }
}

resource "google_cloud_scheduler_job" "clean_cta_bus_stations_job" {
    name             = "clean-cta-bus-stations-job"
    description      = "Triggers the clean-cta-bus-stations-job function every 3 months"
    schedule         = "15 3 1 1,4,7,10 *" # minute 15, 3AM, on the first day, of Jan, Apr, Jul, Oct (every 3 months)
    time_zone        = "America/Chicago"

    http_target {
        http_method = "POST"
        uri         = google_cloudfunctions_function.clean_cta_bus_stations_function.https_trigger_url

        oidc_token {
        service_account_email = google_service_account.scheduler_invoker.email
        }
    }
}