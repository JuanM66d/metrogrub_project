view: master_table_final_v2 {
  sql_table_name: `purple-25-gradient-20250605.master_table_final.master_table_final_v2` ;;


  dimension: doing_business_as_name {
    label: " Business Name"
    type: string
    sql: ${TABLE}.doing_business_as_name ;;
  }
  dimension: final_location_score {
    type: number
    sql: ${TABLE}.final_location_score ;;
  }
  dimension: category {
    type: string
    sql: ${TABLE}.category ;;
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
  dimension: address {
    type: string
    sql: ${TABLE}.address ;;
  }
  dimension: is_food {
    type: number
    sql: ${TABLE}.is_food ;;
  }
  dimension: is_business {
    type: number
    sql: ${TABLE}.is_business ;;
  }
  dimension: is_divvy_station {
    type: number
    sql: ${TABLE}.is_divvy_station ;;
  }
  dimension: station_name {
    label: "Divvy Station"
    type: string
    sql: ${TABLE}.station_name ;;
  }
  dimension: is_bus_stop {
    type: number
    sql: ${TABLE}.is_bus_stop ;;
  }
  dimension: bus_stop {
    label: "Bus Stop"
    type: string
    sql: ${TABLE}.bus_stop ;;
  }
  dimension: foot_traffic_score {
    type: number
    sql: ${TABLE}.foot_traffic_score ;;
  }
  dimension: s2_cell_id {
    type: number
    sql: ${TABLE}.s2_cell_id ;;
  }
  dimension: zone_class {
    type: string
    sql: ${TABLE}.zone_class ;;
  }

  dimension: entity_type {
    type: string
    sql:
    CASE
      WHEN ${is_food} = 1 THEN 'Food'
      WHEN ${is_bus_stop} = 1 THEN 'Bus Stop'
      WHEN ${is_divvy_station} = 1 THEN 'Divvy Station'
      WHEN ${is_business} = 1 THEN 'Business'
      ELSE 'Other'
    END ;;
  }


  measure: count {
    type: count
    drill_fields: [station_name, doing_business_as_name]
  }
}
