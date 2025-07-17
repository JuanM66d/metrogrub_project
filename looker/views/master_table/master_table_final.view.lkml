view: master_table_final {
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

# Add this entire block to your view file

  parameter: location_type_selector {
    group_label: "Filters"
    label: "Select a Location Type"
    description: "Filter the report to a specific type of location. This filter is required."
    type: unquoted
    allowed_value: {
      label: "Business"
      value: "is_business"
    }
    allowed_value: {
      label: "Food"
      value: "is_food"
    }
    allowed_value: {
      label: "Divvy Station"
      value: "is_divvy_station"
    }
    allowed_value: {
      label: "Bus Stop"
      value: "is_bus_stop"
    }
  }

  dimension: is_location_type_selected {
    # This dimension is hidden from users but powers the filter logic
    hidden: no
    type: yesno
    sql:
    -- This CASE statement checks which option the user picked in the parameter
    -- and then checks the corresponding 'yesno' dimension.
    CASE
      WHEN {% parameter location_type_selector %} = 'is_business' THEN ${is_business}
      WHEN {% parameter location_type_selector %} = 'is_food' THEN ${is_food}
      WHEN {% parameter location_type_selector %} = 'is_divvy_station' THEN ${is_divvy_station}
      WHEN {% parameter location_type_selector %} = 'is_bus_stop' THEN ${is_bus_stop}
      ELSE FALSE -- Default case
    END ;;
  }
}
