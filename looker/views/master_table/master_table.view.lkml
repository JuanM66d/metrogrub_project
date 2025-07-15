view: master {
  sql_table_name: master_table.master_table_draft ;;

  # Primary Key (Crucial for data integrity, even if derived)
  # A surrogate key is highly recommended if no natural single or composite key is always unique and non-null.
  # For demonstration, a concatenation is used, but a dedicated auto-incrementing ID column is often better.
  # dimension: unique_record_id {
  #   primary_key: yes
  #   type: string
  #   # This composite key attempts uniqueness, but creating an auto-incrementing ID in your DB is more robust.
  #   sql: CONCAT(COALESCE(${bus_stop_id}, 'NO_BUS_ID'), '-', COALESCE(${divvy_station_id}, 'NO_DIVVY_ID'), '-', COALESCE(${public_nam}, 'NO_NAME'), '-', COALESCE(${street}, 'NO_STREET'), '-', COALESCE(${cross_st}, 'NO_CROSS'), '-', COALESCE(CAST(${year} AS STRING), 'NO_YEAR'), '-', COALESCE(${objectid}, 'NO_OBJ_ID')) ;;
  #   description: "A composite primary key to uniquely identify each record. Consider adding an auto-incrementing ID to your table for a more robust PK."
  # }

  dimension: license_id {
    type: string
    sql: ${TABLE}.license_id ;;
    description: "Unique identifier for the business license."
  }

  dimension: business_name {
    type: string
    sql: ${TABLE}.doing_business_as_name ;;
    description: "The 'Doing Business As' (DBA) name of the business."
  }

  dimension: legal_name {
    type: string
    sql: ${TABLE}.legal_name ;;
    description: "The official legal name of the business."
  }

  dimension: business_activity_id {
    type: number
    sql: ${TABLE}.business_activity_id ;;
    description: "Identifier for the type of business activity."
  }

  dimension: license_description {
    type: string
    sql: ${TABLE}.license_description ;;
    description: "Description of the business license type."
  }

  dimension: business_activity {
    type: string
    sql: ${TABLE}.business_activity ;;
    description: "Detailed description of the business's primary activity."
  }

  dimension: latitude {
    type: number
    sql: ${TABLE}.latitude ;;
    description: "Geographic latitude coordinate of the business location."
  }

  dimension: longitude {
    type: number
    sql: ${TABLE}.longitude ;;
    description: "Geographic longitude coordinate of the business location."
  }

  dimension: city {
    type: string
    sql: ${TABLE}.city ;;
    description: "City where the business is located."
  }

  dimension: address {
    type: string
    sql: ${TABLE}.address ;;
    description: "Street address of the business."
  }

  dimension: zip_code_x {
    type: zipcode
    sql: ${TABLE}.zip_code_x ;;
    description: "Zip code of the business location."
  }


  dimension: location {
    # The 'location' type in LookML can be used for GEOGRAPHY or GEOMETRY types
    # if your database supports it and Looker can interpret it for mapping.
    # Otherwise, you might use 'string' and rely on GIS tools for visualization.
    type: location
    sql_latitude: ${latitude} ;;
    sql_longitude: ${longitude};;
    description: "Geospatial data representing the exact location or shape of the business."
  }

  dimension: food_category {
    type: string
    sql: ${TABLE}.food_category ;;
    description: "Category of food served or sold, if applicable."
  }

  dimension: location_score {
    type: number
    sql: ${TABLE}.location_score ;;
    description: "A calculated score indicating the desirability or quality of the location."
  }

  # --- Boolean Flags ---
  dimension: is_food {
    type: yesno
    sql: ${TABLE}.is_food ;;
    description: "Indicates if the location is related to food services."
  }

  dimension: is_bus_stop {
    type: yesno
    sql: ${TABLE}.is_bus_stop ;;
    description: "Indicates if the record represents a bus stop."
  }

  dimension: is_divvy_station {
    type: yesno
    sql: ${TABLE}.is_divvy_station ;;
    description: "Indicates if the record represents a Divvy station."
  }

  # --- String Identifiers & Names ---
  dimension: bus_stop_id {
    type: string
    sql: ${TABLE}.bus_stop_id ;;
    description: "Unique identifier for the bus stop."
  }

  dimension: street {
    type: string
    sql: ${TABLE}.street ;;
    description: "Street name of the location."
  }

  dimension: cross_st {
    type: string
    sql: ${TABLE}.cross_st ;;
    description: "Cross street name near the location."
  }

  dimension: public_nam {
    type: string
    sql: ${TABLE}.public_nam ;;
    description: "Publicly recognized name of the location or point of interest."
  }

  dimension: divvy_station_id {
    type: string
    sql: ${TABLE}.divvy_station_id ;;
    description: "Unique identifier for the Divvy station."
  }

  dimension: divvy_station_name {
    type: string
    sql: ${TABLE}.station_name ;;
    description: "Name of the Divvy station."
  }

  # --- Numeric Features ---
  dimension: docks_in_service {
    type: number
    sql: ${TABLE}.docks_in_service ;;
    description: "Number of docks currently in service at the Divvy station."
  }

  dimension: year {
    type: number
    sql: ${TABLE}.year ;;
    description: "The year associated with the data record."
  }

  dimension: population_total {
    type: number
    sql: ${TABLE}.population_total ;;
    description: "Total population in the associated demographic area."
  }

  dimension: population_0_to_17 {
    type: number
    sql: ${TABLE}.population_0_to_17 ;;
    description: "Population count for age group 0 to 17."
  }

  dimension: population_18_to_29 {
    type: number
    sql: ${TABLE}.population_18_to_29 ;;
    description: "Population count for age group 18 to 29."
  }

  dimension: population_30_to_39 {
    type: number
    sql: ${TABLE}.population_30_to_39 ;;
    description: "Population count for age group 30 to 39."
  }

  dimension: population_40_to_49 {
    type: number
    sql: ${TABLE}.population_40_to_49 ;;
    description: "Population count for age group 40 to 49."
  }

  dimension: population_50_to_59 {
    type: number
    sql: ${TABLE}.population_50_to_59 ;;
    description: "Population count for age group 50 to 59."
  }

  dimension: population_60_to_69 {
    type: number
    sql: ${TABLE}.population_60_to_69 ;;
    description: "Population count for age group 60 to 69."
  }

  dimension: population_70_to_79 {
    type: number
    sql: ${TABLE}.population_70_to_79 ;;
    description: "Population count for age group 70 to 79."
  }

  dimension: population_80 {
    type: number
    sql: ${TABLE}.population_80 ;;
    description: "Population count for age group 80 and above."
  }

  dimension: population_female {
    type: number
    sql: ${TABLE}.population_female ;;
    description: "Female population count."
  }

  dimension: population_male {
    type: number
    sql: ${TABLE}.population_male ;;
    description: "Male population count."
  }

  dimension: population_latinx {
    type: number
    sql: ${TABLE}.population_latinx ;;
    description: "Latinx population count."
  }

  dimension: population_asian {
    type: number
    sql: ${TABLE}.population_asian ;;
    description: "Asian population count."
  }

  dimension: population_black {
    type: number
    sql: ${TABLE}.population_black ;;
    description: "Black population count."
  }

  dimension: population_white {
    type: number
    sql: ${TABLE}.population_white ;;
    description: "White population count."
  }

  dimension: population_other {
    type: number
    sql: ${TABLE}.population_other ;;
    description: "Population count for other ethnicities."
  }

  dimension: index_right {
    type: number
    sql: ${TABLE}.index_right ;;
    description: "An index column, potentially from a spatial join operation."
  }

  dimension: shape_area {
    type: number
    sql: ${TABLE}.shape_area ;;
    description: "Geographic area of the associated shape or polygon."
  }

  dimension: shape_len {
    type: number
    sql: ${TABLE}.shape_len ;;
    description: "Geographic length of the associated shape or polygon."
  }

  dimension: floor_area_ratio {
    type: number
    sql: ${TABLE}.floor_area_ratio ;;
    description: "Floor Area Ratio (FAR) for the zoning district."
  }

  # --- Geographic/Zoning Identifiers & Descriptions (Strings) ---
  dimension: zip_code_2 {
    type: zipcode
    sql: ${TABLE}.zip_code_2 ;;
    description: "Two-digit zip code."
  }

  dimension: zip_code_y {
    type: zipcode
    sql: ${TABLE}.zip_code_y ;;
    description: "Another zip code column, potentially for different year or purpose."
  }

  dimension: zoning_id {
    type: string
    sql: ${TABLE}.zoning_id ;;
    description: "Unique identifier for the zoning district."
  }

  dimension: zone_class {
    type: string
    sql: ${TABLE}.zone_class ;;
    description: "Classification of the zoning district (e.g., Residential, Commercial)."
  }

  dimension: objectid {
    type: string
    sql: ${TABLE}.objectid ;;
    description: "Geographic Information System (GIS) object identifier."
  }

  dimension: description {
    type: string
    sql: ${TABLE}.description ;;
    description: "General description associated with the record or zoning."
  }

  dimension: district_title {
    type: string
    sql: ${TABLE}.district_title ;;
    description: "Full title of the zoning district."
  }

  dimension: zoning_code_section {
    type: string
    sql: ${TABLE}.zoning_code_section ;;
    description: "Specific section of the zoning code related to this district."
  }

  dimension: maximum_building_height {
    type: string # Stays string if it might contain non-numeric values like 'Unlimited' or 'N/A'
    sql: ${TABLE}.maximum_building_height ;;
    description: "Maximum building height allowed by zoning regulations."
  }

  dimension: lot_area_per_unit {
    type: string # Stays string if it might contain non-numeric values
    sql: ${TABLE}.lot_area_per_unit ;;
    description: "Minimum lot area required per dwelling unit."
  }

  dimension: front_yard_setback {
    type: string # Stays string if it might contain non-numeric values
    sql: ${TABLE}.front_yard_setback ;;
    description: "Minimum front yard setback requirement."
  }

  dimension: side_setback {
    type: string # Stays string if it might contain non-numeric values
    sql: ${TABLE}.side_setback ;;
    description: "Minimum side yard setback requirement."
  }

  dimension: rear_yard_setback {
    type: string # Stays string if it might contain non-numeric values
    sql: ${TABLE}.rear_yard_setback ;;
    description: "Minimum rear yard setback requirement."
  }

  dimension: rear_yard_open_space {
    type: string # Stays string if it might contain non-numeric values
    sql: ${TABLE}.rear_yard_open_space ;;
    description: "Minimum rear yard open space requirement."
  }

  dimension: on_site_open_space {
    type: string # Stays string if it might contain non-numeric values
    sql: ${TABLE}.on_site_open_space ;;
    description: "Minimum on-site open space requirement."
  }

  dimension: minimum_lot_area {
    type: string # Stays string if it might contain non-numeric values
    sql: ${TABLE}.minimum_lot_area ;;
    description: "Minimum lot area required for development."
  }

  dimension: restaurant_allowed {
    type: yesno
    sql: ${TABLE}.restaurant_allowed ;;
    description: "Indicates if restaurants are allowed in the specific zoning district."
  }

  # --- Time Dimension Group ---
  dimension_group: edit_date {
    type: time
    timeframes: [raw, time, date, week, month, quarter, year]
    sql: ${TABLE}.edit_date ;;
    description: "Timestamp of the last edit or update to the record."
  }

  # --- Measures (for aggregation and quick analysis) ---
  measure: count {
    type: count
    drill_fields: [public_nam, street, cross_st, zip_code_y]
    description: "Count of records in the dataset."
  }

  measure: total_docks_in_service {
    type: sum
    sql: ${docks_in_service} ;;
    description: "Total number of docks reported in service."
  }

  measure: avg_docks_in_service {
    type: average
    sql: ${docks_in_service} ;;
    description: "Average number of docks in service."
  }

  measure: sum_population_total {
    type: sum
    sql: ${population_total} ;;
    description: "Sum of total population across selected records."
  }

  measure: avg_floor_area_ratio {
    type: average
    sql: ${floor_area_ratio} ;;
    description: "Average Floor Area Ratio."
  }

}
