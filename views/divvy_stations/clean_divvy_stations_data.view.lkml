# The name of this view in Looker is "Clean Divvy Stations Data"
view: clean_divvy_stations_data {
  # The sql_table_name parameter indicates the underlying database table
  # to be used for all fields in this view.
  sql_table_name: `divvy_stations.clean_divvy_stations_data` ;;

  # No primary key is defined for this view. In order to join this view in an Explore,
  # define primary_key: yes on a dimension that has no repeated values.

    # Here's what a typical dimension looks like in LookML.
    # A dimension is a groupable field that can be used to filter query results.
    # This dimension will be called "Divvy Station ID" in Explore.

  dimension: divvy_station_id {
    type: string
    sql: ${TABLE}.divvy_station_id ;;
  }

  dimension: docks_in_service {
    type: number
    sql: ${TABLE}.docks_in_service ;;
  }

  dimension: latitude {
    type: number
    sql: ${TABLE}.latitude ;;
  }

  dimension: location {
    type: string
    sql: ${TABLE}.location ;;
  }

  dimension: location_coordinates {
    type: string
    sql: ${TABLE}.location_coordinates ;;
  }

  dimension: location_type {
    type: string
    sql: ${TABLE}.location_type ;;
  }

  dimension: longitude {
    type: number
    sql: ${TABLE}.longitude ;;
  }

  dimension: station_name {
    type: string
    sql: ${TABLE}.station_name ;;
  }

  dimension: status {
    type: string
    sql: ${TABLE}.status ;;
  }

  dimension: total_docks {
    type: number
    sql: ${TABLE}.total_docks ;;
  }
  measure: count {
    type: count
    drill_fields: [station_name]
  }
}
