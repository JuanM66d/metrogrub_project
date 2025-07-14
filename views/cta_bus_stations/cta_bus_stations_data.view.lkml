# The name of this view in Looker is "Cta Bus Stations Data"
view: cta_bus_stations_data {
  # The sql_table_name parameter indicates the underlying database table
  # to be used for all fields in this view.
  sql_table_name: `cta_bus_stations.cta_bus_stations_data` ;;

  # No primary key is defined for this view. In order to join this view in an Explore,
  # define primary_key: yes on a dimension that has no repeated values.

    # Here's what a typical dimension looks like in LookML.
    # A dimension is a groupable field that can be used to filter query results.
    # This dimension will be called "City" in Explore.

  dimension: city {
    type: string
    sql: ${TABLE}.city ;;
  }

  dimension: cross_st {
    type: string
    sql: ${TABLE}.cross_st ;;
  }

  dimension: dir {
    type: string
    sql: ${TABLE}.dir ;;
  }

  dimension: latitude {
    type: number
    sql: ${TABLE}.latitude ;;
  }

  dimension: longitude {
    type: number
    sql: ${TABLE}.longitude ;;
  }

  dimension: pos {
    type: string
    sql: ${TABLE}.pos ;;
  }

  dimension: public_nam {
    type: string
    sql: ${TABLE}.public_nam ;;
  }

  dimension: routesstpg {
    type: string
    sql: ${TABLE}.routesstpg ;;
  }

  dimension: street {
    type: string
    sql: ${TABLE}.street ;;
  }

  dimension: systemstop {
    type: string
    sql: ${TABLE}.systemstop ;;
  }
  measure: count {
    type: count
  }
}
