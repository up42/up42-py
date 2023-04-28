# Tasking

Request a satellite or an aircraft to capture your designated area with certain criteria, such as processing levels and data specifications.

## Step 1. Choose a tasking collection

1. Use the `get_data_products` function to choose a [tasking collection](https://docs.up42.com/data/datasets) and get its `data_product_id` for ordering:
  ```python
  tasking = up42.initialize_tasking()
  products = tasking.get_data_products(basic=True)
  print(products)
  ```
  An example of one tasking collection in the response:
  ```json
  {
     "Pléiades Neo Tasking":{
        "collection": "pneo-tasking",
        "host": "oneatlas",
        "data_products": {
           "Custom": "07c33a51-94b9-4509-84df-e9c13ea92b84",
           "Analytic (Mono)": "123eabab-0511-4f36-883a-80928716c3db",
           "Display (Mono)": "469f9b2f-1631-4c09-b66d-575abd41dc8f"
        }
     }
  }
  ```

2. Choose a data product and copy its ID:
  ```python
  data_product_id = "123eabab-0511-4f36-883a-80928716c3db"
  ```

## Step 2. Request tasking access

If you want to order the chosen collection for the first time, you need to request access to it. For more information on access requests, see [Restrictions](https://docs.up42.com/getting-started/restrictions#tasking-collections).

An email from the Customer Success team usually takes up to 3 days. You can review your access request status on the [Access requests](https://console.up42.com/settings/access) page.

## Step 3. Accept an EULA

If you want to order the chosen collection for the first time, you need to accept its EULA. For more information on license agreements, see [Account management](https://docs.up42.com/getting-started/account/management#accept-end-user-license-agreements).

## Step 4. Get a JSON schema of an order form

Get detailed information about the parameters needed to create an order for the chosen data product by using `tasking.get_data_product_schema(data_product_id)`, for example:
```python
tasking.get_data_product_schema("123eabab-0511-4f36-883a-80928716c3db")
```

## Step 5. Fill out the order form

1. Specify geometry and use the required request body schema format for the chosen data product, for example:
  ```python
  # geometry = up42.read_vector_file("data/aoi_washington.geojson")
  geometry = {
      "type": "Polygon",
      "coordinates": (
          (
              (13.375966, 52.515068),
              (13.375966, 52.516639),
              (13.378314, 52.516639),
              (13.378314, 52.515068),
              (13.375966, 52.515068),
          ),
      ),
  }

  order_parameters = tasking.construct_order_parameters(
      data_product_id="123eabab-0511-4f36-883a-80928716c3db",
      name="PNeo tasking order",
      acquisition_start="2023-11-01",
      acquisition_end="2023-12-20",
      geometry=geometry,
  )
  ```
  The returned log will contain the required parameters you'll need to specify:
  ```text
  2023-04-27 16:54:24,397 - As `acquisitionMode` select one of ['mono']
  2023-04-27 16:54:24,398 - As `cloudCoverage` select `{'description': 'Maximum allowed cloud coverage in percentage.', 'minimum': 5, 'maximum': 20, 'type': 'integer'}`
  2023-04-27 16:54:24,399 - As `geometricProcessing` select one of ['ortho']
  ```

1. Update the request by adding the requested parameters, for example:
  ```python
  order_parameters["params"].update({
      "acquisitionMode": "mono",
      "cloudCoverage": "10",
      "geometricProcessing": "ortho"
  })
  ```

1. Check the parameters by printing them:
  ```python
  print(order_parameters)
  ```

## Step 6. Place an order

If multiple people need to be alerted about a future order, create a group email and [add it to the account](https://docs.up42.com/getting-started/account/management#change-your-email) you'll be placing an order with. Otherwise, only one person will receive notifications about it.

Use the `tasking.place_order` function to place your order:
```python
order = tasking.place_order(order_parameters)
order
```

If you've defined an AOI with multiple geometries, each geometry will create a separate order. Order names will be suffixed with incrementing numbers: `Order 1`, `Order 2`, etc.

## Step 7. Review feasibility

After an order is placed, the Operations team will look at the order feasibility. They will evaluate the tasking parameters with the provider, and then will present the following assessments:

- The order is possible with the given parameters.
- The order requires modifications with suitable options proposed.

You will receive an email notifying you when your order feasibility has been assessed. To proceed, follow these steps:

1. Open the [console](https://console.up42.com) and go to **Tasking** → **My orders**.
2. Select your order and click **Feasibility**.
3. Choose a suitable option. If none of the options are suitable, [contact](https://up42.com/company/contact-ordering) the Operations team.
4. Click **Confirm** chosen option.

You can't modify your order after accepting an option.

## Step 8. Activate an order

After selecting an option, you will receive a price quote for your order. To review a price quote and activate your order, follow these steps:

1. Open the [console](https://console.up42.com) and go to **Tasking** → **My orders**.
2. Select your order and click **Price**.
3. Accept or reject this price. If you accept, the amount will be deducted from your credit balance and tasking operations will start.

## Step 9. Monitor an order

Check the status of your order:
```python
order.status
```