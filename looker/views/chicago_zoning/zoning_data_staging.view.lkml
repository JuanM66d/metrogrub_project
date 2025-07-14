# The name of this view in Looker is "Zoning Data Staging"
view: zoning_data_staging {
  # The sql_table_name parameter indicates the underlying database table
  # to be used for all fields in this view.
  sql_table_name: `chicago_zoning.zoning_data_staging` ;;

  # No primary key is defined for this view. In order to join this view in an Explore,
  # define primary_key: yes on a dimension that has no repeated values.

    # Here's what a typical dimension looks like in LookML.
    # A dimension is a groupable field that can be used to filter query results.
    # This dimension will be called "Case Number" in Explore.

  dimension: case_number {
    type: string
    sql: ${TABLE}.case_number ;;
  }
  # Dates and timestamps can be represented in Looker using a dimension group of type: time.
  # Looker converts dates and timestamps to the specified timeframes within the dimension group.

  dimension_group: create {
    type: time
    timeframes: [raw, time, date, week, month, quarter, year]
    sql: ${TABLE}.create_date ;;
  }

  dimension_group: edit {
    type: time
    timeframes: [raw, time, date, week, month, quarter, year]
    sql: ${TABLE}.edit_date ;;
  }

  dimension: edit_uid {
    type: string
    sql: ${TABLE}.edit_uid ;;
  }

  dimension: geometry {
    type: string
    sql: ${TABLE}.geometry ;;
  }

  dimension: globalid {
    type: string
    sql: ${TABLE}.globalid ;;
  }

  dimension: objectid {
    type: string
    sql: ${TABLE}.objectid ;;
  }

  dimension: override_r {
    type: string
    sql: ${TABLE}.override_r ;;
  }

  dimension: pd_num {
    type: string
    sql: ${TABLE}.pd_num ;;
  }

  dimension: shape_area {
    type: number
    sql: ${TABLE}.shape_area ;;
  }

  dimension: shape_len {
    type: number
    sql: ${TABLE}.shape_len ;;
  }

  dimension: zone_class {
    type: string
    sql: ${TABLE}.zone_class ;;
  }

  dimension: zone_type {
    type: string
    sql: ${TABLE}.zone_type ;;
  }

  dimension: zoning_id {
    type: string
    sql: ${TABLE}.zoning_id ;;
  }
  measure: count {
    type: count
  }
}
