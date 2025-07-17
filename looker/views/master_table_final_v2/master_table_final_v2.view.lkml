view: master_table_final_v2 {
  sql_table_name: `purple-25-gradient-20250605.master_table_final.master_table_final_v2` ;;

  dimension: address {
    type: string
    sql: ${TABLE}.address ;;
  }
  dimension: bus_stop {
    type: string
    sql: ${TABLE}.bus_stop ;;
  }
  dimension: category {
    type: string
    sql: ${TABLE}.category ;;
  }
  dimension: doing_business_as_name {
    type: string
    sql: ${TABLE}.doing_business_as_name ;;
  }
  dimension: final_location_score {
    type: number
    sql: ${TABLE}.final_location_score ;;
  }
  dimension: foot_traffic_score {
    type: number
    sql: ${TABLE}.foot_traffic_score ;;
  }
  dimension: is_bus_stop {
    type: number
    sql: ${TABLE}.is_bus_stop ;;
  }
  dimension: is_business {
    type: number
    sql: ${TABLE}.is_business ;;
  }
  dimension: is_divvy_station {
    type: number
    sql: ${TABLE}.is_divvy_station ;;
  }
  dimension: is_food {
    type: number
    sql: ${TABLE}.is_food ;;
  }
  dimension: latitude {
    type: number
    sql: ${TABLE}.latitude ;;
  }
  dimension: longitude {
    type: number
    sql: ${TABLE}.longitude ;;
  }
  dimension: location {
    type: location
    sql_latitude: ${latitude};;
    sql_longitude: ${longitude} ;;
  }
  dimension: s2_cell_id {
    type: number
    sql: ${TABLE}.s2_cell_id ;;
  }
  dimension: station_name {
    type: string
    sql: ${TABLE}.station_name ;;
  }
  dimension: zone_class {
    type: string
    sql: ${TABLE}.zone_class ;;
  }
  measure: count {
    type: count
    drill_fields: [station_name, doing_business_as_name]
  }
}
