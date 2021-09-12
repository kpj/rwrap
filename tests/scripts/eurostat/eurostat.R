library(tidyverse)
library(eurostat)


df_geo <- get_eurostat_geospatial(
    output_class = "sf", resolution = 60, nuts_level = 2, year = 2016
)

# make comparison with Python object possible by converting geometry to string
df_geo %>%
    mutate(
        geometry = sf::st_as_text(geometry)
    ) %>%
    write_csv("result.csv")
