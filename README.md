# uAgents A2A Adapter

Convert any Agentverse uAgent into an A2A-compatible service

This adapter allows any A2A client to communicate with Agentverse uAgents by creating a standard A2A agent card and handling protocol translation.

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install the Package

```bash
# Install from source (recommended for development)
git clone <repository-url>
cd uagents-a2a-adapter
pip install -e .
```

After installation, the `uagents-a2a` CLI command will be available globally.

## Architecture & Communication Flow

### What Gets Created
When you run the adapter, two separate components are created:

1. **A2A Server** (your chosen port, default: 10000)
   - HTTP server exposing A2A protocol endpoints
   - Created by `main.py`
   - Handles A2A client requests

2. **Bridge uAgent** (port 8082)
   - uAgent that communicates with Agentverse
   - Created by `agentverse_agent_executor.py`
   - Bridges A2A requests to chat protocol

3. **Target uAgent** (existing)
   - Your chosen Agentverse uAgent (unchanged)
   - Receives chat messages via Agentverse mailbox

### Communication Flow

```
┌─────────────┐    HTTP/A2A     ┌─────────────┐    Internal     ┌─────────────┐    Chat Protocol    ┌─────────────┐
│             │ ──────────────→ │             │ ──────────────→ │             │ ─────────────────→  │             │
│ A2A Client  │                 │ A2A Server  │                 │ Bridge      │                     │ Target      │
│ (curl/app)  │ ←────────────── │ (port 10000)│ ←────────────── │ uAgent      │ ←─────────────────  │ uAgent      │
│             │   HTTP Response │             │    Response     │ (port 8082) │   Chat Response     │ (Agentverse)│
└─────────────┘                 └─────────────┘                 └─────────────┘                     └─────────────┘
```

### Step-by-Step Flow

1. A2A Client sends HTTP request to http://localhost:10000
2. A2A Server receives request, extracts user query
3. A2A Server calls `agentverse_agent_executor.py`
4. Bridge uAgent sends ChatMessage to target agent via Agentverse
5. Target uAgent processes query, sends ChatMessage response
6. Bridge uAgent receives response, caches it
7. A2A Server streams response back to A2A client

**Key Point**: The A2A Server (port 10000) is what A2A clients connect to. The Bridge uAgent (port 8082) is internal infrastructure that handles the Agentverse communication.
<img width="896" alt="Screenshot 2025-07-08 at 10 54 16 PM" src="https://github.com/user-attachments/assets/6727d59a-1a12-48f4-a6d9-307c4dad414e" />


## What This Does

- **Input**: Any Agentverse uAgent address
- **Output**: Running HTTP server with A2A endpoints and agent card
- **Result**: Any A2A client can discover and use the uAgent

### What You Get:

- **HTTP Server**: `http://localhost:10000` with A2A protocol endpoints
- **Agent Card**: `http://localhost:10000/.well-known/agent.json` for discovery
- **Bridge Connection**: Automatically forwards A2A requests to your chosen uAgent
- **Standard Interface**: Your uAgent now appears as a regular A2A agent to external clients

## Quick Start

### Step 1: Get Target Agent Address
Find the Agentverse uAgent you want to use (e.g., `agent1qdv2qgxucvqatam6nv28qp202f3pw8xqpfm8man6zyegztuzd2t6yem9evl`)

### Step 2: Run the Adapter

Using the CLI command:

```bash
uagents-a2a --agent-address "agent1qdv2qgxucvqatam6nv28qp202f3pw8xqpfm8man6zyegztuzd2t6yem9evl"
```

With custom options:

```bash
uagents-a2a \
  --host localhost \
  --port 9001 \
  --agent-address "agent1qdv2qgxucvqatam6nv28qp202f3pw8xqpfm8man6zyegztuzd2t6yem9evl" \
  --agent-name "Finance Q&A Agent" \
  --agent-description "Provides explanation on various finance terms" \
  --skill-tags "finance,explanation,terms" \
  --skill-examples "what is a stock, how to trade, what is a bond"
```

### Step 3: Expected Output

```
INFO:uagents_a2a_adapter.main:Starting A2A server bridged to Agentverse agent: agent1qdv2qgxucvqatam6nv28qp202f3pw8xqpfm8man6zyegztuzd2t6yem9evl
INFO:     [a2a_agentverse_bridge]: Starting agent with address: agent1qtmxvc3lp8qn9jtq4w22xw27ygx9qvuzme85un6cdn9r4v8fxszs5d4rsr2
INFO:uagents_a2a_adapter.agentverse_agent_executor:A2A Bridge agent started with address: agent1qtmxvc3lp8qn9jtq4w22xw27ygx9qvuzme85un6cdn9r4v8fxszs5d4rsr2
INFO:uagents_a2a_adapter.agentverse_agent_executor:Target Agentverse agent: agent1qdv2qgxucvqatam6nv28qp202f3pw8xqpfm8man6zyegztuzd2t6yem9evl
INFO:     [a2a_agentverse_bridge]: Agent inspector available at https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8082&address=agent1qtmxvc3lp8qn9jtq4w22xw27ygx9qvuzme85un6cdn9r4v8fxszs5d4rsr2
INFO:uagents_a2a_adapter.agentverse_agent_executor:✅ A2A Bridge to Agentverse started successfully
INFO:uagents_a2a_adapter.main:🚀 A2A server starting on localhost:9001
INFO:uagents_a2a_adapter.main:🔗 Bridging to Agentverse agent: agent1qdv2qgxucvqatam6nv28qp202f3pw8xqpfm8man6zyegztuzd2t6yem9evl
INFO:uagents_a2a_adapter.main:📋 Agent name: Finance Q&A Agent
INFO:     Uvicorn running on http://localhost:9001 (Press CTRL+C to quit)
```

### Step 4: Connect Bridge Agent

1. Click on the Agent Inspector link from the terminal output
2. Click **Connect** button
3. Select **Mailbox**
4. Click **Finish**

### Step 5: Test with A2A Client

#### Option A: Using Curl

```bash
curl -X POST http://localhost:9001 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-1",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [
          {
            "kind": "text",
            "text": "What is a stock?"
          }
        ],
        "messageId": "msg-1"
      },
      "contextId": "ctx-123"
    }
  }'
```

#### Option B: Using the Test Client

Run the included test client:

```bash
python examples/test_client.py
```

Or the simplified Perplexity client:

```bash
python examples/test_perplexity_client.py
```

## Programmatic Usage

You can also use the adapter programmatically in your Python code:

```python
from uagents_a2a_adapter import A2ARegisterTool

# Initialize the adapter
adapter = A2ARegisterTool()

# Start the A2A server
config = {
    "agent_address": "agent1qdv2qgxucvqatam6nv28qp202f3pw8xqpfm8man6zyegztuzd2t6yem9evl",
    "host": "localhost",
    "port": 9001,
    "agent_name": "My Agent",
    "agent_description": "Custom agent description"
}

result = adapter.invoke(config)
print(f"Server started at: {result['endpoint']}")

# Server runs in background thread
# Your application can continue with other tasks
```

## CLI Options

| Option | Required | Description |
|--------|----------|-------------|
| `--agent-address` | Yes | Agentverse uAgent address |
| `--agent-name` | No | Display name for A2A agent |
| `--agent-description` | No | Description for A2A agent |
| `--skill-tags` | No | Comma-separated skill tags |
| `--skill-examples` | No | Comma-separated example queries |
| `--host` | No | Host (default: localhost) |
| `--port` | No | Port (default: 10000) |

## Examples

### Currency Agent
```bash
uagents-a2a \
  --agent-address "agent1qv3yr66aw2qu3gzce5ckae84uj8ea5hua90q9mzwxcr9ghvtv0xeykme4dv" \
  --agent-name "Currency Exchange Agent" \
  --skill-tags "currency,exchange,rates"
```

### GitHub Agent
```bash
uagents-a2a \
  --agent-address "agent1qv7uuldfcrp3f3y6309amaspr2e8f26g7qhh2lln62n2ssa04ugzk9rsw4" \
  --agent-name "GitHub MCP Agent" \
  --skill-tags "github,git,repository,code"
```

### Perplexity Research Agent
```bash
uagents-a2a \
  --agent-address "agent1qdv2qgxucvqatam6nv28qp202f3pw8xqpfm8man6zyegztuzd2t6yem9evl" \
  --agent-name "Perplexity Research Agent" \
  --agent-description "AI-powered research and web search capabilities"
  --skill-tags "research,search,web,perplexity,ai"
  --skill-examples "Latest AI developments,Research quantum computing,What happened today?"
```

## Package Structure

```
uagents_a2a_adapter/
├── __init__.py                     # Package exports
├── main.py                         # CLI and A2A server
├── adapter.py                      # Programmatic API (A2ARegisterTool)
└── agentverse_agent_executor.py    # Core bridge logic

examples/
├── test_client.py                  # Full-featured test client
├── test_perplexity_client.py       # Simplified test client
└── perplexity_agent_example.py     # Perplexity agent example
```

## How It Works

```
A2A Client → Bridge A2A Server → Bridge Agent → Agentverse → Target uAgent
     ↑            (port 9001)      (port 8082)    (mailbox)     (your chosen agent)
Any A2A client                                                     
can discover                                                       
and use the agent
```

1. **Bridge A2A Server** (port 9001): Exposes standard A2A endpoints
2. **Bridge Agent** (port 8082): Handles communication with Agentverse via mailbox
3. **Target Agent**: The Agentverse uAgent you specified

## Features

### What Gets Created

- **A2A Agent Card** at `http://localhost:9001/.well-known/agent.json`
- **A2A Endpoints** for message sending and receiving
- **Bridge Agent** that connects to Agentverse via mailbox
- **Protocol Translation** between A2A and uAgent chat protocol
- **Session Persistence** with multi-user support via context IDs

### Key Benefits

- ✅ **Zero Modification**: Use existing Agentverse uAgents without changes
- ✅ **Standard A2A Protocol**: Full compatibility with A2A clients
- ✅ **Auto Discovery**: Agents are discoverable via standard agent cards
- ✅ **Multi-User Support**: Handle multiple concurrent users
- ✅ **Session Persistence**: Maintain conversation context
- ✅ **Simple Setup**: Just provide an agent address and run

## Troubleshooting

### Common Issues

1. **Port Conflicts**: If default port 10000 is in use, specify a different port:
   ```bash
   uagents-a2a --agent-address <address> --port 9001
   ```

2. **Agent Not Responding**: Ensure the target agent is active on Agentverse and connected to mailbox

3. **Timeout Issues**: Some queries may timeout due to network latency or agent processing time. This is normal for complex queries.

4. **Bridge Connection**: Make sure to connect the bridge agent via the Inspector link shown in the logs

## Dependencies

The package automatically installs these dependencies:

- `a2a>=0.44` - A2A protocol implementation
- `uvicorn` - ASGI server for HTTP endpoints
- `click` - CLI framework
- `httpx` - Async HTTP client
- `python-dotenv` - Environment variable management
- `uagents` - uAgents framework
- `uagents-core` - Core uAgents functionality

Now any A2A client can discover your uAgent and communicate with it using standard A2A protocol!
