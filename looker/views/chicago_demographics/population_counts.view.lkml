# The name of this view in Looker is "Population Counts"
view: population_counts {
  # The sql_table_name parameter indicates the underlying database table
  # to be used for all fields in this view.
  sql_table_name: `chicago_demographics.population_counts` ;;

  # No primary key is defined for this view. In order to join this view in an Explore,
  # define primary_key: yes on a dimension that has no repeated values.

    # Here's what a typical dimension looks like in LookML.
    # A dimension is a groupable field that can be used to filter query results.
    # This dimension will be called "Geography Type" in Explore.

  dimension: geography_type {
    type: string
    sql: ${TABLE}.geography_type ;;
  }

  dimension: population_0_to_17 {
    type: number
    sql: ${TABLE}.population_0_to_17 ;;
  }

  dimension: population_18_to_29 {
    type: number
    sql: ${TABLE}.population_18_to_29 ;;
  }

  dimension: population_30_to_39 {
    type: number
    sql: ${TABLE}.population_30_to_39 ;;
  }

  dimension: population_40_to_49 {
    type: number
    sql: ${TABLE}.population_40_to_49 ;;
  }

  dimension: population_50_to_59 {
    type: number
    sql: ${TABLE}.population_50_to_59 ;;
  }

  dimension: population_60_to_69 {
    type: number
    sql: ${TABLE}.population_60_to_69 ;;
  }

  dimension: population_70_to_79 {
    type: number
    sql: ${TABLE}.population_70_to_79 ;;
  }

  dimension: population_80 {
    type: number
    sql: ${TABLE}.population_80 ;;
  }

  dimension: population_asian {
    type: number
    sql: ${TABLE}.population_asian ;;
  }

  dimension: population_black {
    type: number
    sql: ${TABLE}.population_black ;;
  }

  dimension: population_female {
    type: number
    sql: ${TABLE}.population_female ;;
  }

  dimension: population_latinx {
    type: number
    sql: ${TABLE}.population_latinx ;;
  }

  dimension: population_male {
    type: number
    sql: ${TABLE}.population_male ;;
  }

  dimension: population_other {
    type: number
    sql: ${TABLE}.population_other ;;
  }

  dimension: population_total {
    type: number
    sql: ${TABLE}.population_total ;;
  }

  dimension: population_white {
    type: number
    sql: ${TABLE}.population_white ;;
  }

  dimension: record_id {
    type: string
    sql: ${TABLE}.record_id ;;
  }

  dimension: year {
    type: number
    sql: ${TABLE}.year ;;
  }

  dimension: zip_code {
    type: zipcode
    sql: ${TABLE}.zip_code ;;
  }
  measure: count {
    type: count
  }
}
