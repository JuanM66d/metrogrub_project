# Define the database connection to be used for this model.
connection: "purple_big_query"

# include all the views
include: "/looker/views/**/*.view.lkml"

# Datagroups define a caching policy for an Explore. To learn more,
# use the Quick Help panel on the right to see documentation.

datagroup: metrogrub_data_default_datagroup {
  # sql_trigger: SELECT MAX(id) FROM etl_log;;
  max_cache_age: "1 hour"
}

persist_with: metrogrub_data_default_datagroup

explore: foot_traffic {
  from: yearly_average
}

explore: transportation {
  from: clean_cta_bus_stations
}
