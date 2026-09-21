# Data source

The pipeline fetches the ONS [Local Authority District to Region (December 2024)
lookup in England](https://www.data.gov.uk/dataset/3fbe9109-f329-4c4a-85cb-3b78ea4fbce3/local-authority-district-to-region-december-2024-lookup-in-en)
on every import. It contains 296 authorities in 9 regions. This is a fixed
historical geography, not a current UK-wide database.

[View the source JSON](https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/LAD24_RGN24_EN_LU/FeatureServer/0/query?where=1%3D1&outFields=LAD24CD%2CLAD24NM%2CRGN24CD%2CRGN24NM&returnGeometry=false&orderByFields=LAD24CD&f=json).
The fields are authority code/name (`LAD24CD`, `LAD24NM`) and region code/name
(`RGN24CD`, `RGN24NM`). No manual download or API key is required.

Source: Office for National Statistics licensed under the
[Open Government Licence v.3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
See [ONS licensing guidance](https://www.ons.gov.uk/methodology/geography/licences).
