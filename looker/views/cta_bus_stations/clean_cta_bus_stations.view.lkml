# The name of this view in Looker is "Clean Cta Bus Stations"
view: clean_cta_bus_stations {
  # The sql_table_name parameter indicates the underlying database table
  # to be used for all fields in this view.
  sql_table_name: `cta_bus_stations.clean_cta_bus_stations` ;;

  # No primary key is defined for this view. In order to join this view in an Explore,
  # define primary_key: yes on a dimension that has no repeated values.

    # Here's what a typical dimension looks like in LookML.
    # A dimension is a groupable field that can be used to filter query results.
    # This dimension will be called "Bus Stop ID" in Explore.

  dimension: bus_stop_id {
    type: string
    sql: ${TABLE}.bus_stop_id ;;
  }

  dimension: city {
    type: string
    sql: ${TABLE}.city ;;
  }

  dimension: cross_st {
    type: string
    sql: ${TABLE}.cross_st ;;
  }

  dimension: geometry {
    type: string
    sql: ${TABLE}.geometry ;;
  }

  dimension: latitude {
    type: number
    sql: ${TABLE}.latitude ;;
  }

  dimension: longitude {
    type: number
    sql: ${TABLE}.longitude ;;
  }

  dimension: public_nam {
    type: string
    sql: ${TABLE}.public_nam ;;
  }

  dimension: street {
    type: string
    sql: ${TABLE}.street ;;
  }
  measure: count {
    type: count
  }
}
