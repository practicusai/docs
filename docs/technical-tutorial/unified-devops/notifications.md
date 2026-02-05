---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: practicus
    language: python
    name: python3
---

# Sending Notifications

This example demonstrates how to use the optional (but recommended) Practicus AI notify app. If installed, the notify app can be used to send emails, and if configured, SMS, and other notifications. It also supports auto-populating exception details so that error notifications can be sent automatically.

In the examples below, you'll see two common use cases:

1. **Sample Notification:** Send a test email with custom parameters.
2. **Exception Notification:** Automatically send an email with exception details when an error occurs.

### Example 1: Sending an email

In this example, the notify app sends a test email. You can specify recipients, title, body, and additional parameters such as log level, category, and urgency.

- `recipients = None` Sends email to current user.
- `recipients = 'user@company.com'` Sends email to selected user.
- `recipients = ['user@company.com', .. ]` Sends email to selected users.

```python
# Parameters:
recipients = None
```

```python
assert recipients, "Please enter your recipients."
```

```python
import practicuscore as prt

prt.notify.send(
    recipients=recipients,
    title="Sample notification",
    body="This is a sample notification..",
    level="info",
    category="sample_notification",
    urgency="normal",
    # Add email attachments by setting attachment_paths.
    # Safe file types and max size (default 20MB) are defined by admin.
    # Zip files if file type is restricted.
    # attachment_paths=["path/to/file1.txt, path/to/file2.md"]
    # View help for other customizations
)
print("Test email sent")
```

### Example 2: Sending Exception Notifications

In this example, we simulate an exception. The notify app captures exception details (such as the stack trace) and sends an email notification automatically when `exc_info=True`. This is useful for auto-alerting in production environments when unexpected errors occur.

```python
import practicuscore as prt

try:
    # Let's simulate an exception
    x = 1 / 0
except:
    prt.notify.send(exc_info=True)
    print("Exception notification sent to current user.")
```

## Conclusion

This example demonstrated how to use the Practicus AI notify app to send both test notifications and automatic error alerts with exception details. You can integrate this functionality into your applications to ensure critical issues are reported immediately.

Feel free to extend these examples or integrate the notify feature into your own Practicus AI applications.


---

**Previous**: [Build Custom Images](build-custom-images.md) | **Next**: [Operations Guide > Getting Started](../operations-guide/getting-started.md)
