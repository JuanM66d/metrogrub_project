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