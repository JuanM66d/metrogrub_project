# The name of this view in Looker is "Clean Active Business Licenses"
view: clean_active_business_licenses {
  # The sql_table_name parameter indicates the underlying database table
  # to be used for all fields in this view.
  sql_table_name: `chicago_active_business_licenses.clean_active_business_licenses` ;;

  # No primary key is defined for this view. In order to join this view in an Explore,
  # define primary_key: yes on a dimension that has no repeated values.

    # Here's what a typical dimension looks like in LookML.
    # A dimension is a groupable field that can be used to filter query results.
    # This dimension will be called "Address" in Explore.

  dimension: address {
    type: string
    sql: ${TABLE}.address ;;
  }

  dimension: business_activity {
    type: string
    sql: ${TABLE}.business_activity ;;
  }

  dimension: business_activity_id {
    type: string
    sql: ${TABLE}.business_activity_id ;;
  }

  dimension: category {
    type: string
    sql: ${TABLE}.category ;;
  }

  dimension: city {
    type: string
    sql: ${TABLE}.city ;;
  }

  dimension: doing_business_as_name {
    type: string
    sql: ${TABLE}.doing_business_as_name ;;
  }

  dimension: fake_location_score {
    type: number
    sql: ${TABLE}.fake_location_score ;;
  }

  dimension: latitude {
    type: number
    sql: ${TABLE}.latitude ;;
  }

  dimension: legal_name {
    type: string
    sql: ${TABLE}.legal_name ;;
  }

  dimension: license_description {
    type: string
    sql: ${TABLE}.license_description ;;
  }

  dimension: license_id {
    type: string
    sql: ${TABLE}.license_id ;;
  }

  dimension: location {
    type: string
    sql: ${TABLE}.location ;;
  }

  dimension: longitude {
    type: number
    sql: ${TABLE}.longitude ;;
  }

  dimension: state {
    type: string
    sql: ${TABLE}.state ;;
  }

  dimension: zip_code {
    type: zipcode
    sql: ${TABLE}.zip_code ;;
  }
  measure: count {
    type: count
    drill_fields: [doing_business_as_name, legal_name]
  }
}
