# 🪝 Webhooks

In this chapter you will learn how to setup webhooks on UP42 via the Python SDK. When a new order or job is finished,
the webhook sends a signal to a selected HTTPS url which can be used to e.g. trigger additional operations 
on your end. Also see the [full webhook documentation](https://docs.up42.com/account/webhooks) and accompanying 
[blogpost](https://up42.com/blog/tech/first-step-into-webhooks-no-code-required).

## **Authenticate**

First connect with UP42 as explained in the [authentication chapter](authentication.md).

```python
import up42
up42.authenticate(project_id="your project ID", project_api_key="your-project-API-key")
```

## **Manage existing webhooks**

Query existing webhooks in your UP42 workspace to modify, test or delete the resulting webhook object, see the [webhook
code reference](webhooks-reference.md) for all available functionality.

```python
webhooks = up42.get_webhooks()
webhooks[0].trigger_test_event()
```

## **Create a new webhook**

```python
events = up42.get_webhook_events() #[e.g. "job.status", "order.status"]
webhook = up42.create_webhook(name="new-webhook", url="https://receiving-url.com", events=events, active=True)
webhook.trigger_test_event()
```
