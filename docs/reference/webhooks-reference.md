# Webhooks

The Webhooks class enables creation and modification of custom event notifications with [webhooks](webhooks.md).

```python
webhook = up42.initialize_webhook(webhook_id="1df1ebb0-78a4-55d9-b806-15d22e391bd3")
```

A webhook is a method for sending event notifications from one application to another. When something happens in a source system indicated by an event, the webhook transmits an event notification via HTTPS to a specific URL.

You can set up webhooks to receive notifications in the following cases:

- **Job status updates**. Every time a [job status](../../reference/job-reference/#status) changes.
- **Order status updates**. When a new [order](../../reference/order-reference/#status) is completed — successfully or not.

For more information about creating a webhook, view the UP42 [webhooks documentation](https://docs.up42.com/account/webhooks)

## Webhooks

### info

The `info` attribute returns metadata of a specific webhook.

The returned format is `dict`

<h5> Example </h5>

```python
webhook.info
```

### get_webhooks()

The `get_webhooks()` function returns all registered webhooks for this workspace.

```python
get_webhooks(return_json)
```

The returned format is `list[Webhook]`.

<h5> Arguments </h5>

| Argument      | Overview                                                                                                                                                               |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `return_json` | **bool**<br/>Determines how to return webhooks:<br/><ul><li>`True`: return JSON.</li><li>`False`: return webhook class objects.</li></ul>The default value is `False`. |

<h5> Example </h5>

```python
webhooks = up42.get_webhooks(return_json=False)
```

### create_webhook()

The `create_webhook()` function allows you to register a new webhook in the system.

```python
create_webhook(
    name,
    url,
    events,
    active,
    secret,
)
```

The returned format is `Webhook`.

<h5> Arguments </h5>

| Argument | Overview                                                                                                                                                                                    |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`   | **str / required**<br/>The webhook name.                                                                                                                                                    |
| `url`    | **str / required**<br/>A unique URL where the webhook will send the message. HTTPS is required.                                                                                             |
| `events` | **list[str]**<br/>A list of events that trigger the webhook. The allowed values:<br/><ul><li>`job.status`</li><li>`order.status`</li></ul>                                                  |
| `active` | **bool**<br/>Determines whether the webhook is active after creation:<br/><ul><li>`True`: webhook is active.</li><li>`False`: webhook is not active.</li></ul>The default value is `False`. |
| `secret` | **optional[str]**<br/>The secret used to generate webhook signatures. The default value is `None`.                                                                                          |

<h5> Example </h5>

```python
webhook = up42.create_webhook(
    name="new-webhook",
    url="https://receiving-url.com",
    events=["job.status", "order.status"],
    active=True,
    secret="QWZTFnMEXhqZKNmu",
)
```

### update()

The `update()` function allows you to modify a specific webhook.

```python
update(
    name,
    url,
    events,
    active,
    secret,
)
```

The returned format is `dict`.

<h5> Arguments </h5>

| Argument | Overview                                                                                                                                                      |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`   | **str**<br/>An updated webhook name.                                                                                                                          |
| `url`    | **str**<br/>An updated unique URL where the webhook will send the message. HTTPS is required.                                                                 |
| `events` | **list[str]**<br/>An updated list of events that trigger the webhook. The allowed values:<br/><ul><li>`job.status`</li><li>`order.status`</li></ul>           |
| `active` | **bool**<br/>An updated webhook status:<br/><ul><li>`True`: webhook is active.</li><li>`False`: webhook is not active.</li></ul>The default value is `False`. |
| `secret` | **optional[str]**<br/>An updated secret used to generate webhook signatures. The default value is `None`.                                                     |

<h5> Example </h5>

```python
webhook.update(
    name="new-name",
    active=False,
)
```

### delete()

The `delete()` function allows you to delete a registered webhook.

```python
delete()
```

<h5> Example </h5>

```python
webhook.delete()
```

## Events

### get_webhook_events()

The `get_webhook_events()` function returns all available webhook events.

```python
get_webhook_events()
```

The returned format is `dict`.

<h5> Example </h5>

```python
up42.get_webhook_events()
```

### trigger_test_events()

The `trigger_test_events()` allows you to trigger a webhook test event to test your receiving side. The UP42 server will send test messages for each subscribed event to the specified webhook URL.

```python
trigger_test_events()
```

The returned format is `dict`.

<h5> Example </h5>

```python
webhook.trigger_test_events()
```
