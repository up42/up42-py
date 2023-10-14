# Webhooks

A [webhook](https://docs.up42.com/getting-started/webhooks) is a method for sending event notifications from one application to another. When something happens in a source system indicated by an event, the webhook transmits an event notification via HTTPS to a specific URL.

## See notification events

You can set up webhooks to receive notifications in the following cases:

- **Job status updates.** Every time a job changes its status.
- **Order status updates.** When a new order has been completed — successfully or not.

```python
events = up42.get_webhook_events()
print(events)
```

## Create and test a new webhook

```python
webhook = up42.create_webhook(
    name="new-webhook",
    url="https://receiving-url.com",
    events=events,
    active=True
)
webhook.trigger_test_event()
```

## Manage existing webhooks

Modify you webhook:
```python
webhooks = up42.get_webhooks()
webhooks[0].update(
    name="new-webhook",
    url="https://receiving-url.com",
    events=events,
    active=False
)
```

Delete your webhook:
```python
webhooks = up42.get_webhooks()
webhooks[0].delete()
```

## Learn more

- [First step into UP42 webhooks: Almost no code required](https://up42.com/blog/first-step-into-webhooks-no-code-required)
