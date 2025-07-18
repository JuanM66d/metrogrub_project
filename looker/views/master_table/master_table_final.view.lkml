view: master {
  sql_table_name: `purple-25-gradient-20250605.master_table_final.master_table_final` ;;

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
  dimension: city {
    type: string
    sql: ${TABLE}.city ;;
  }
  dimension: business_name {
    type: string
    sql: ${TABLE}.doing_business_as_name ;;
  }
  dimension: fake_location_score {
    type: number
    sql: ${TABLE}.fake_location_score ;;
  }
  dimension: foot_traffic_score {
    type: number
    sql: ${TABLE}.foot_traffic_score ;;
  }
  dimension: location {
    type: location
    sql_latitude: ${latitude};;
    sql_longitude: ${longitude} ;;
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
  dimension: zipcode {
    type: string
    sql: ${TABLE}.location ;;
  }
  dimension: longitude {
    type: number
    sql: ${TABLE}.longitude ;;
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
  dimension: population_total {
    type: number
    sql: ${TABLE}.population_total ;;
  }
  dimension: state {
    type: string
    sql: ${TABLE}.state ;;
  }
  dimension: station_name {
    type: string
    sql: ${TABLE}.station_name ;;
  }
  dimension: total_docks {
    type: number
    sql: ${TABLE}.total_docks ;;
  }
  dimension: zip_code {
    type: zipcode
    sql: ${TABLE}.zip_code ;;
  }
  dimension: zone_class {
    type: string
    sql: ${TABLE}.zone_class ;;
  }
  measure: count {
    type: count
    drill_fields: [station_name, business_name]
  }
}
