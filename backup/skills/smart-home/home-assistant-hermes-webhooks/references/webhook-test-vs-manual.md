# hermes webhook test vs Manual Testing

**Discovered:** 2026-06-17 during pill-reminder webhook testing

## Key Difference

The `hermes webhook test <name>` CLI command and manual webhook calls use **different signature validation paths**:

| Aspect | `hermes webhook test` | Manual / HA shell_command |
|--------|----------------------|---------------------------|
| **Header** | `X-Hub-Signature-256` | `X-Webhook-Signature` |
| **Format** | `sha256=<hex>` (GitHub-style) | Raw hex HMAC-SHA256 |
| **Payload** | `{test: true, event_type: "test", message: "Hello from hermes webhook test"}` | Whatever you send (typically `b"{}"`) |
| **Secret used** | Route secret from subscription | Route secret from subscription |

## Why This Matters

- The test command **always passes** (it constructs the correct GitHub-style signature internally)
- Manual calls with `X-Webhook-Signature` **fail with 401** if you use the global config secret instead of the route secret
- Both validation paths use the **same route secret**, just different header formats

## Debugging Tip

When `hermes webhook test` works but your HA automation gets 401:

1. Check you're using `X-Webhook-Signature` header (not `X-Hub-Signature-256` or `X-Hermes-Signature`)
2. Verify the secret matches the **route secret** from `hermes webhook subscribe` / `hermes webhook list`
3. Ensure payload bytes are identical: `b"{}"` in Python, not `"{}"` or `json.dumps({})`

## Log Evidence

```
# Gateway logs show both paths:
[webhook] direct-deliver event=test route=pill-reminder target=telegram  ← test command (200)
[webhook] Invalid signature for route pill-reminder                       ← manual call with wrong header/secret (401)
```

## Validation Code Path (gateway/platforms/webhook.py)

1. Checks for Svix headers (`svix-id`, `svix-timestamp`, `svix-signature`)
2. Checks for GitHub: `X-Hub-Signature-256` = `sha256=<hex>`
3. Checks for GitLab: `X-Gitlab-Token` = plain secret
4. **Checks for Generic: `X-Webhook-Signature` = raw hex HMAC-SHA256** ← HA scripts use this
5. If secret configured but no recognized header → reject