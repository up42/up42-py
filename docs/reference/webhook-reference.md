# Webhook

The Webhook class enables you to view, test, and modify custom event notifications with [webhooks](webhooks.md).

```python
webhook = up42.initialize_webhook(webhook_id="d290f1ee-6c54-4b01-90e6-d701748f0851")
```
To learn how to create a webhook, see the [up42 class](up42-reference.md).

## Webhooks

### info

The `info` attribute returns metadata of a specific webhook.

The returned format is `dict`

<h5> Example </h5>

```python
webhook.info
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

| Argument | Overview                                                                                                                                                                                  |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`   | **str**<br/>The name of the webhook.                                                                                                                                                      |
| `url`    | **str**<br/>The URL of the webhook.                                                                                                                                                       |
| `events` | **list[str]**<br/>A list of events that trigger the webhook. The allowed values are as follows:<br/><ul><li>`job.status`</li><li>`order.status`</li></ul>                                                |
| `active` | **bool**<br/>Whether this webhook should be active after the update:<br/><ul><li>`True`: webhook is active.</li><li>`False`: webhook isn't active.</li></ul>The default value is `False`. |
| `secret` | **str**<br/>The secret used to generate webhook signatures.                                                                                                                               |

<h5> Example </h5>

```python
webhook.update(
    name="new-name",
    url="https://new-receiving-url.com",
    events=["job.status"],
    active=True,
    secret="RFZTJnNAChqZKNmo",
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
