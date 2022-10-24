# :satellite: **Create a Satellite Tasking Order**

A basic example on how to create a tasking order on UP42.

## **Authenticate**

First connect with UP42 as explained in the [authentication chapter](authentication.md).

```python
import up42
up42.authenticate(project_id="your project ID", project_api_key="your-project-API-key")
```

## **Decide on the satellite dataset**

We look at the available data products and decide to create a tasking order for a TerraSar satellite image (
[see marketplace](https://up42.com/marketplace/data/tasking/terra-sar-tasking)). The `get_data_products` function 
gives us the `collection` name and the `data_product_id` (required for ordering).

```python
tasking = up42.initialize_tasking()
products = tasking.get_data_products(basic=True)
print(products)
```

```json
{
  "Pléiades Tasking": {"collection": "PHR-tasking",
    "host": "oneatlas",
    "data_products": {"Custom": "4f866cd3-d816-4c98-ace3-e6105623cf13",
      "Analytic": "bd102407-1814-4f92-8b5a-7697b7a73f5a",
      "Display": "28d4a077-6620-4ab5-9a03-c96bf622457e"}},
  "TerraSAR Tasking": {"collection": "terra-sar-tasking",
    "host": "airbus",
    "data_products": {"Custom": "a6f64332-3148-4e05-a475-45a02176f210"}}
}
```

```python
terrasar_product_id = "a6f64332-3148-4e05-a475-45a02176f210"
```

## **Create the order parameters**

```python
#geometry = up42.read_vector_file("data/aoi_washington.geojson")
geometry = {"type": "Polygon",
   "coordinates": (((13.375966, 52.515068),
     (13.375966, 52.516639),
     (13.378314, 52.516639),
     (13.378314, 52.515068),
     (13.375966, 52.515068)),)}
```

To help with the order parameters we can use `tasking.construct_order_parameters`.


```python
order_parameters = tasking.construct_order_parameters(data_product_id=terrasar_product_id,
                                                      name="My Terrasar tasking order",
                                                      start_date= "2022-10-12",
                                                      end_date= "2022-10-19",
                                                      geometry=geometry)
```

```text
log: As `acquisitionMode` select one of ['spotlight', 'staring_spotlight', 'stripmap', ...]
log: As `polarization` select one of ['hh', 'vv', 'vh', 'hv', 'hh_vv', 'vv_vh', 'hh_hv']
log: As `processingLevel` select one of ['ssc', 'mgd', 'gec', 'eec']
```

```python
order_parameters["params"].update({
    "acquisitionMode": "spotlight",
    "polarization": "hh",
    "processingLevel": "ssc"
})
print(order_parameters)
```

```json
{"dataProduct": "38ac8357-18c2-454d-acb5-9ec8f4c043b9",
 "params": {"displayName": "My Terrasar tasking order",
  "acquisitionStart": "2022-10-12T00:00:00Z",
  "acquisitionEnd": "2022-10-19T23:59:59Z",
  "geometry": {"type": "Polygon",
   "coordinates": (((13.375966, 52.515068),
     (13.375966, 52.516639),
     (13.378314, 52.516639),
     (13.378314, 52.515068),
     (13.375966, 52.515068)),)},
  "acquisitionMode": "spotlight",
  "polarization": "hh",
  "processingLevel": "ssc"}}
```

## **Place the tasking order**

After placing the tasking order, UP42 will carry out a feasibility study for the specified requirements and contact you
with next steps via email.

```python
order = tasking.place_order(order_parameters)
order
```

You can check the status of the tasking order in code or on the UP42 Console, in the Storage menu under the "Orders" 
tab.

```python
order.status
```

## **Feasibility study**

After the order placed, the UP42 customer support team will reach out to you via email with the results of the
tasking feasibility study and pricing options.