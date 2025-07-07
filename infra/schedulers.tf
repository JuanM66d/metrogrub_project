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
