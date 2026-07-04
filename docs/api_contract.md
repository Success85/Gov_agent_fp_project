# API Contract

This is the agreed shape of each endpoint. Lane 1 builds to this; Lane 5 tests against it.
If either side changes it, update this file and tell the other person.

## POST /chat

Sends a citizen's question and returns the assistant's grounded reply.

**Request (JSON):**
```json
{
  "question": "Ni ibihe byangombwa nsaba indangamuntu?"
}
```

**Response (JSON):**
```json
{
  "reply": "Kugira ngo usabe indangamuntu ukeneye..."
}
```

**Status codes:**
- 200 — success, reply returned
- 422 — the request was missing the "question" field

## GET /

Health check. Returns `{ "status": "Gov Agent API is running" }` with status 200.