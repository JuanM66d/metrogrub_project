# The name of this view in Looker is "Clean Zoning Data"
view: clean_zoning_data {
  # The sql_table_name parameter indicates the underlying database table
  # to be used for all fields in this view.
  sql_table_name: `chicago_zoning.clean_zoning_data` ;;

  # No primary key is defined for this view. In order to join this view in an Explore,
  # define primary_key: yes on a dimension that has no repeated values.

  # Dates and timestamps can be represented in Looker using a dimension group of type: time.
  # Looker converts dates and timestamps to the specified timeframes within the dimension group.

  dimension_group: edit {
    type: time
    timeframes: [raw, time, date, week, month, quarter, year]
    sql: ${TABLE}.edit_date ;;
  }
    # Here's what a typical dimension looks like in LookML.
    # A dimension is a groupable field that can be used to filter query results.
    # This dimension will be called "Geometry" in Explore.

  dimension: geometry {
    type: string
    sql: ${TABLE}.geometry ;;
  }

  dimension: objectid {
    type: string
    sql: ${TABLE}.objectid ;;
  }

  dimension: restaurant_allowed {
    type: number
    sql: ${TABLE}.restaurant_allowed ;;
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

  dimension: zoning_id {
    type: string
    sql: ${TABLE}.zoning_id ;;
  }
  measure: count {
    type: count
  }
}
