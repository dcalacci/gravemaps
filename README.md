# gravemaps

A graphql server and associated python code to create nice-looking list-maps of the graveyards in a
bounding box. Here's an example, from boston.

To run:

```bash
pip install -r requirements.txt
cd server/ && python server.py
```

Then, navigate to http://127.0.0.1:5000/graphql, and put in a query, like this:

```graphql
mutation {
  submitMap(
    xmin: -71.1929535654
    xmax: -70.9781663877
    ymax: 42.4024328423
    ymin: 42.2912856611
    mapType: LEGEND
    nGraveyards: SMALL
  ) {
    id
    imageUrl
    nGraveyards
  }
}
```

![gravemap-boston](./notebooks/bbox_cemetery.png)

To create your own map of another area, either use the python code itself (example in `notebooks/`),
or leverage the graphql api:
