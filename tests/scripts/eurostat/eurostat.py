import re
from shapely import wkt
from rwrap import eurostat


df_geo = eurostat.get_eurostat_geospatial(
    output_class="sf", resolution=60, nuts_level=2, year=2016
)

# iron out some formatting issues
df_geo["geometry"] = df_geo["geometry"].apply(
    lambda x: re.sub(
        r"\.([ ,)])",
        r"\1",
        re.sub(r"0+([ ,)])", r"\1", wkt.dumps(x, rounding_precision=5)),
    )
)

df_geo.to_csv("result.csv", index=False)
