# The name of this view in Looker is "Active Business Licenses"
view: active_business_licenses {
  # The sql_table_name parameter indicates the underlying database table
  # to be used for all fields in this view.
  sql_table_name: `chicago_active_business_licenses.active_business_licenses` ;;

  # No primary key is defined for this view. In order to join this view in an Explore,
  # define primary_key: yes on a dimension that has no repeated values.

    # Here's what a typical dimension looks like in LookML.
    # A dimension is a groupable field that can be used to filter query results.
    # This dimension will be called "Account Number" in Explore.

  dimension: account_number {
    type: string
    sql: ${TABLE}.account_number ;;
  }

  dimension: address {
    type: string
    sql: ${TABLE}.address ;;
  }
  # Dates and timestamps can be represented in Looker using a dimension group of type: time.
  # Looker converts dates and timestamps to the specified timeframes within the dimension group.

  dimension_group: application_requirements_complete {
    type: time
    timeframes: [raw, time, date, week, month, quarter, year]
    sql: ${TABLE}.application_requirements_complete ;;
  }

  dimension: application_type {
    type: string
    sql: ${TABLE}.application_type ;;
  }

  dimension: business_activity {
    type: string
    sql: ${TABLE}.business_activity ;;
  }

  dimension: business_activity_id {
    type: string
    sql: ${TABLE}.business_activity_id ;;
  }

  dimension: city {
    type: string
    sql: ${TABLE}.city ;;
  }

  dimension: community_area {
    type: string
    sql: ${TABLE}.community_area ;;
  }

  dimension: community_area_name {
    type: string
    sql: ${TABLE}.community_area_name ;;
  }

  dimension: conditional_approval {
    type: string
    sql: ${TABLE}.conditional_approval ;;
  }

  dimension_group: date_issued {
    type: time
    timeframes: [raw, time, date, week, month, quarter, year]
    sql: ${TABLE}.date_issued ;;
  }

  dimension: doing_business_as_name {
    type: string
    sql: ${TABLE}.doing_business_as_name ;;
  }

  dimension_group: expiration {
    type: time
    timeframes: [raw, time, date, week, month, quarter, year]
    sql: ${TABLE}.expiration_date ;;
  }

  dimension: id {
    type: string
    sql: ${TABLE}.id ;;
  }

  dimension: latitude {
    type: number
    sql: ${TABLE}.latitude ;;
  }

  dimension: legal_name {
    type: string
    sql: ${TABLE}.legal_name ;;
  }

  dimension_group: license_approved_for_issuance {
    type: time
    timeframes: [raw, time, date, week, month, quarter, year]
    sql: ${TABLE}.license_approved_for_issuance ;;
  }

  dimension: license_code {
    type: string
    sql: ${TABLE}.license_code ;;
  }

  dimension: license_description {
    type: string
    sql: ${TABLE}.license_description ;;
  }

  dimension: license_id {
    type: string
    sql: ${TABLE}.license_id ;;
  }

  dimension: license_number {
    type: string
    sql: ${TABLE}.license_number ;;
  }

  dimension_group: license_start {
    type: time
    timeframes: [raw, time, date, week, month, quarter, year]
    sql: ${TABLE}.license_start_date ;;
  }

  dimension: license_status {
    type: string
    sql: ${TABLE}.license_status ;;
  }

  dimension: location {
    type: string
    sql: ${TABLE}.location ;;
  }

  dimension: longitude {
    type: number
    sql: ${TABLE}.longitude ;;
  }

  dimension: neighborhood {
    type: string
    sql: ${TABLE}.neighborhood ;;
  }

  dimension_group: payment {
    type: time
    timeframes: [raw, time, date, week, month, quarter, year]
    sql: ${TABLE}.payment_date ;;
  }

  dimension: police_district {
    type: string
    sql: ${TABLE}.police_district ;;
  }

  dimension: precinct {
    type: string
    sql: ${TABLE}.precinct ;;
  }

  dimension: site_number {
    type: string
    sql: ${TABLE}.site_number ;;
  }

  dimension: state {
    type: string
    sql: ${TABLE}.state ;;
  }

  dimension: ward {
    type: string
    sql: ${TABLE}.ward ;;
  }

  dimension: ward_precinct {
    type: string
    sql: ${TABLE}.ward_precinct ;;
  }

  dimension: zip_code {
    type: zipcode
    sql: ${TABLE}.zip_code ;;
  }
  measure: count {
    type: count
    drill_fields: [legal_name, community_area_name, doing_business_as_name]
  }
}
