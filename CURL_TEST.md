# Local curl tests (Streamable HTTP)

## Health check

```bash
curl -s http://localhost:8080/health | jq
```

## MCP endpoint (send email via tools/call)

`/mcp` uses JSON-RPC. Use `Content-Type: application/json` and `Accept: application/json, text/event-stream`.

### 1. Initialize (optional, to check server response)

```bash
curl -s -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": { "name": "curl", "version": "1.0" }
    }
  }' | jq
```

### 2. Call tool: send_system_alert

Replace `YOUR_EMAIL@example.com` with the recipient.

```bash
curl -s -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": "2",
    "method": "tools/call",
    "params": {
      "name": "send_system_alert",
      "arguments": {
        "receiver_email": "YOUR_EMAIL@example.com"
      }
    }
  }' | jq
```

### 3. Call tool: send_email (custom subject/body)

```bash
curl -s -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": "3",
    "method": "tools/call",
    "params": {
      "name": "send_email",
      "arguments": {
        "receiver_email": "YOUR_EMAIL@example.com",
        "subject": "Test from curl",
        "body": "Hello, this is a test."
      }
    }
  }' | jq
```

**Note:** If the server returns SSE (stream) instead of JSON, the response may be chunked. For a full MCP handshake (initialize → initialized → call_tool) in one session, use:

```bash
python test_send_email.py
```

with `server_url = "http://localhost:8080/mcp"` in the script.
