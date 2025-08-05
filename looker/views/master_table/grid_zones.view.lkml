view: grid_zones {
  sql_table_name: `purple-25-gradient-20250605.master_table_final.grid_zones` ;;

  dimension: avg_location_score {
    type: number
    sql: ${TABLE}.avg_location_score ;;
    label: "Unscaled Location Score"
  }
  dimension: rescaled_location_score {
    type: number
    sql: ${TABLE}.rescaled_score ;;
    label: "Average Location Score: "
  }
  dimension: bus_stop_count {
    label: "Bus Stops: "
    type: number
    sql: ${TABLE}.bus_stop_count ;;
  }
  dimension: business_count {
    label: "Businesses: "
    type: number
    sql: ${TABLE}.business_count ;;
  }
  dimension: divvy_station_count {
    label: "Divvy Stations: "
    type: number
    sql: ${TABLE}.divvy_station_count ;;
  }
  dimension: lat_grid {
    type: number
    value_format_name: id
    sql: ${TABLE}.lat_grid ;;
  }
  dimension: lon_grid {
    type: number
    value_format_name: id
    sql: ${TABLE}.lon_grid ;;
  }
  dimension: restaurant_count {
    label: "Restaurants: "
    type: number
    sql: ${TABLE}.restaurant_count ;;
  }
  dimension: total_locations {
    type: number
    sql: ${TABLE}.total_locations ;;
  }
  dimension: zone_id {
    label: "ZONE ID"
    primary_key: yes
    type: number
    sql: zone_id ;;
    map_layer_name: location_zones
  }

  measure: count {
    type: count
  }
}
