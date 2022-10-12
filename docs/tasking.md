# :satellite: **Create Satellite Tasking Order**

A basic example on how to create a tasking order on UP42.

## **Authenticate**

First connect with UP42 as explained in the [authentication chapter](authentication.md).

```python
import up42
up42.authenticate(project_id="your project ID", project_api_key="your-project-API-key")
```

## **Decide on dataset / sensor**

We look at the available data products and decide to create a tasking order for a TerraSar satellite image (
[see marketplace](https://up42.com/marketplace/data/tasking/terra-sar-tasking)).<br>
The `get_data_products` function gives us the `collection` name and the `data_product_id` (required for ordering).

```python
tasking = up42.initialize_tasking()
products = tasking.get_data_products(basic=True)
products
```

```python
terrasar_product_id = "38ac8357-18c2-454d-acb5-9ec8f4c043b9"
```

```python
geometry = {"type": "Polygon",
   "coordinates": (((13.375966, 52.515068),
     (13.375966, 52.516639),
     (13.378314, 52.516639),
     (13.378314, 52.515068),
     (13.375966, 52.515068)),)}
```

```python
order_parameters = tasking.construct_order_parameters(data_product_id=terrasar_product_id,
                                                      name="My Terrasar tasking order",
                                                      start_date= "2022-10-12",
                                                      end_date= "2022-10-19",
                                                      geometry=geometry)

# Parameters specific to this data_product
order_parameters["params"]["acquisitionMode"] = "spotlight"
order_parameters["params"]["polarization"] = "hh"
order_parameters["params"]["processingLevel"] = "ssc"

order_parameters
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
with next steps via email. You can see the status of the tasking order on the UP42 Console, in the Storage menu under the "Orders" tab.

```python
order = tasking.place_order(order_parameters)
order
```

## **Feasibility study**

After the order placed, the UP42 customer support team will reach out to you via email with the results of the
tasking feasibility study and pricing options.