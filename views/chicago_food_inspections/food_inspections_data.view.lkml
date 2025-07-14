# The name of this view in Looker is "Food Inspections Data"
view: food_inspections_data {
  # The sql_table_name parameter indicates the underlying database table
  # to be used for all fields in this view.
  sql_table_name: `chicago_food_inspections.food_inspections_data` ;;

  # No primary key is defined for this view. In order to join this view in an Explore,
  # define primary_key: yes on a dimension that has no repeated values.

    # Here's what a typical dimension looks like in LookML.
    # A dimension is a groupable field that can be used to filter query results.
    # This dimension will be called "Address" in Explore.

  dimension: address {
    type: string
    sql: ${TABLE}.address ;;
  }

  dimension: aka_name {
    type: string
    sql: ${TABLE}.aka_name ;;
  }

  dimension: city {
    type: string
    sql: ${TABLE}.city ;;
  }

  dimension: dba_name {
    type: string
    sql: ${TABLE}.dba_name ;;
  }

  dimension: facility_type {
    type: string
    sql: ${TABLE}.facility_type ;;
  }
  # Dates and timestamps can be represented in Looker using a dimension group of type: time.
  # Looker converts dates and timestamps to the specified timeframes within the dimension group.

  dimension_group: inspection {
    type: time
    timeframes: [raw, time, date, week, month, quarter, year]
    sql: ${TABLE}.inspection_date ;;
  }

  dimension: inspection_id {
    type: string
    sql: ${TABLE}.inspection_id ;;
  }

  dimension: inspection_type {
    type: string
    sql: ${TABLE}.inspection_type ;;
  }

  dimension: latitude {
    type: number
    sql: ${TABLE}.latitude ;;
  }

  dimension: license_ {
    type: string
    sql: ${TABLE}.license_ ;;
  }

  dimension: location {
    type: string
    sql: ${TABLE}.location ;;
  }

  dimension: longitude {
    type: number
    sql: ${TABLE}.longitude ;;
  }

  dimension: results {
    type: string
    sql: ${TABLE}.results ;;
  }

  dimension: risk {
    type: string
    sql: ${TABLE}.risk ;;
  }

  dimension: state {
    type: string
    sql: ${TABLE}.state ;;
  }

  dimension: violations {
    type: string
    sql: ${TABLE}.violations ;;
  }

  dimension: zip {
    type: zipcode
    sql: ${TABLE}.zip ;;
  }
  measure: count {
    type: count
    drill_fields: [dba_name, aka_name]
  }
}
