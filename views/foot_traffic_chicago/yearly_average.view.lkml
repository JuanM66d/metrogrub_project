# The name of this view in Looker is "Yearly Average"
view: yearly_average {
  # The sql_table_name parameter indicates the underlying database table
  # to be used for all fields in this view.
  sql_table_name: `foot_traffic_chicago.yearly_average` ;;

  # No primary key is defined for this view. In order to join this view in an Explore,
  # define primary_key: yes on a dimension that has no repeated values.

    # Here's what a typical dimension looks like in LookML.
    # A dimension is a groupable field that can be used to filter query results.
    # This dimension will be called "Latitude" in Explore.

  dimension: latitude {
    type: number
    sql: ${TABLE}.latitude ;;
  }

  dimension: longitude {
    type: number
    sql: ${TABLE}.longitude ;;
  }

  dimension: yearly_average_foot_traffic {
    type: number
    sql: ${TABLE}.yearly_average_foot_traffic ;;
  }
  measure: count {
    type: count
  }
}
