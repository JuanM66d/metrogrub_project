view: master_table_final_v3 {
  sql_table_name: `purple-25-gradient-20250605.master_table_final.master_table_final_v3` ;;

  dimension: address {
    type: string
    sql: ${TABLE}.address ;;
  }
  dimension: category {
    type: string
    sql: INITCAP(REPLACE(${TABLE}.category, '_', ' '));;
  }
  dimension: entity_name {
    type: string
    sql: ${TABLE}.entity_name ;;
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
  dimension: license_id {
    type: string
    sql: ${TABLE}.license_id ;;
  }
  dimension: location {
    type: location
    sql_latitude: ${latitude};;
    sql_longitude: ${longitude} ;;
  }
  dimension: longitude {
    type: number
    sql: ${TABLE}.longitude ;;
  }
  dimension: restaurant_allowed_flag {
    type: number
    sql: ${TABLE}.restaurant_allowed_flag ;;
  }
  dimension: s2_cell_id {
    type: number
    sql: ${TABLE}.s2_cell_id ;;
  }
  dimension: zone_class {
    type: string
    sql: ${TABLE}.zone_class ;;
  }
  measure: count {
    type: count
    drill_fields: [entity_name]
  }
}
