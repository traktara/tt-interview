# Location data for the map task

Use this ONS dataset for locations:

[Download England local authority locations as JSON](https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/Local_Authority_Districts_December_2024_Boundaries_UK_BGC/FeatureServer/0/query?where=LAD24CD%20LIKE%20%27E%25%27&outFields=LAD24CD,LAD24NM,LAT,LONG&returnGeometry=false&orderByFields=LAD24CD&f=json).

The response contains a `features` array. Each feature's `attributes` contains:

| Field | Meaning |
| --- | --- |
| `LAD24CD` | Authority code; matches `code` in the app's authority data |
| `LAD24NM` | Authority name |
| `LAT` | Latitude |
| `LONG` | Longitude |

Source: Office for National Statistics. See the
[source layer and attribution](https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/Local_Authority_Districts_December_2024_Boundaries_UK_BGC/FeatureServer/0?f=pjson).
