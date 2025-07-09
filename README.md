# uAgents A2A Adapter

Convert any Agentverse uAgent into an A2A-compatible service

This adapter allows any A2A client to communicate with Agentverse uAgents by creating a standard A2A agent card and handling protocol translation.

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install the Package

```bash
# Install from PyPI (recommended)
pip install uagents-a2a-adapter
```

#### Development Installation

```bash
# Install from source (for development)
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

<img width="896" alt="Screenshot 2025-07-08 at 10 54 16 PM" src="https://github.com/user-attachments/assets/f73df0b0-46c2-4f95-802b-77fa3c937327" />

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

Get started in **3 simple steps** with our complete Currency Exchange example:

### Step 1: Run the Currency uAgent

First, start the currency exchange uAgent:

```bash
# Navigate to the example
cd examples/currency-exchange-agent

# Install dependencies (if needed)
pip install langchain-google-genai python-dotenv

# Set your Google API key
export GOOGLE_API_KEY="your-google-api-key"

# Run the currency uAgent
python currency_uagent.py
```

The agent will start and display its address:
```
INFO: Currency Exchange Agent started
INFO: Agent address: agent1q...
INFO: Agent running on port 8007
```

### Step 2: Start the A2A Adapter

Copy the agent address from the logs and start the A2A adapter:

```bash
# Use the agent address from Step 1
uagents-a2a \
  --agent-address "agent1q..." \
  --agent-name "Currency Exchange Agent" \
  --agent-description "Real-time currency exchange rates with natural language processing" \
  --skill-tags "currency,exchange,rates,finance" \
  --skill-examples "Convert USD to EUR,What is the exchange rate for GBP to JPY,100 dollars to euros"
```

#### Expected Output

You'll see the A2A adapter start successfully:

```
INFO:uagents_a2a_adapter.main:Starting A2A server bridged to Agentverse agent: agent1q...
INFO:     [a2a_agentverse_bridge]: Starting agent with address: agent1qtm...
INFO:uagents_a2a_adapter.agentverse_agent_executor:A2A Bridge agent started with address: agent1qtm...
INFO:uagents_a2a_adapter.agentverse_agent_executor:Target Agentverse agent: agent1q...
INFO:     [a2a_agentverse_bridge]: Agent inspector available at https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8082&address=agent1qtm...
INFO:uagents_a2a_adapter.agentverse_agent_executor:✅ A2A Bridge to Agentverse started successfully
INFO:uagents_a2a_adapter.main:🚀 A2A server starting on localhost:10000
INFO:uagents_a2a_adapter.main:🔗 Bridging to Agentverse agent: agent1q...
INFO:uagents_a2a_adapter.main:📋 Agent name: Currency Exchange Agent
INFO:     Uvicorn running on http://localhost:10000 (Press CTRL+C to quit)
```

#### Connect Bridge Agent to Agentverse

1. Click on the **Agent Inspector link** from the terminal output
2. Click **Connect** button
3. Select **Mailbox**
4. Click **Finish**

### Step 3: Test with A2A Clients

#### Option A: Using the Test Client

Run the included test client in a new terminal:

```bash
# In a new terminal
python examples/test_currencyExchange_client.py
```

You'll see various currency exchange queries and responses:

```
📤 Query: Convert 100 USD to EUR
✅ Response: The current exchange rate from USD to EUR is 0.85441. 
    So 100 USD equals approximately 85.44 EUR.

📤 Query: What is the GBP to JPY rate?
✅ Response: The current exchange rate from GBP to JPY is 156.789
    British Pounds to Japanese Yen.

📤 Query: 500 euros to dollars
✅ Response: Converting 500 EUR to USD at the current rate of 1.17002
    equals approximately 585.01 USD.
```

#### Option B: Using Curl

You can also test directly with curl:

```bash
curl -X POST http://localhost:10000 \
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
            "text": "Convert 100 USD to EUR"
          }
        ],
        "messageId": "msg-1"
      },
      "contextId": "ctx-123"
    }
  }'
```

Expected response:
```json
{
  "jsonrpc": "2.0",
  "id": "test-1",
  "result": {
    "response": {
      "role": "assistant",
      "parts": [
        {
          "kind": "text",
          "text": "The current exchange rate from USD to EUR is 0.85441. So 100 USD equals approximately 85.44 EUR."
        }
      ]
    }
  }
}
```

### ✅ That's It!

You now have a **complete A2A-compatible currency exchange service** running! The workflow demonstrates:

- ✅ **Natural Language Processing**: "Convert 100 dollars to euros"
- ✅ **Real-time Exchange Rates**: Live data from Frankfurter API
- ✅ **LangChain Integration**: Google Gemini for query understanding
- ✅ **uAgent Messaging**: Complete uAgent-to-uAgent communication
- ✅ **A2A Protocol**: Standard JSON-RPC over HTTP
- ✅ **Session Persistence**: Context maintained across queries



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



## Other Example Agents

You can also adapt the A2A bridge to work with other Agentverse agents:

### Financial Q&A Agent
```bash
uagents-a2a \
  --agent-address "agent1qfjjdp5nnvxqtfcusfn9qhk7zv5k2jm2mq0zu3vfnf0p8q9mwj9zx6zv8p" \
  --agent-name "Financial Q&A Agent" \
  --agent-description "Financial markets analysis and investment guidance" \
  --skill-tags "finance,investment,markets,analysis" \
  --skill-examples "What are government bonds?,Explain cryptocurrency market,Investment strategies for 2024"
```

### Perplexity Research Agent
```bash
uagents-a2a \
  --agent-address "agent1qgzd0c60d4c5n37m4pzuclv5p9vwsftmfkznksec3drux8qnhmvuymsmshp" \
  --agent-name "Perplexity Research Agent" \
  --agent-description "AI-powered research and web search capabilities" \
  --skill-tags "research,search,web,perplexity,ai" \
  --skill-examples "Latest AI developments,Research quantum computing,What happened today?"
```

### GitHub Agent
```bash
uagents-a2a \
  --agent-address "agent1qv7uuldfcrp3f3y6309amaspr2e8f26g7qhh2lln62n2ssa04ugzk9rsw4" \
  --agent-name "GitHub MCP Agent" \
  --skill-tags "github,git,repository,code"
```

## Package Structure

```
uagents_a2a_adapter/
├── __init__.py                     # Package exports  
├── main.py                         # CLI and A2A server
├── adapter.py                      # Programmatic API (A2ARegisterTool)
└── agentverse_agent_executor.py    # Core bridge logic

examples/
├── currency-exchange-agent/
│   ├── currency_uagent.py          # Complete currency uAgent with LangChain
│   └── agent.py                    # Currency processing logic
└── test_currencyExchange_client.py # A2A test client for currency queries
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
- `a2a-sdk>=0.2.8` - A2A SDK for uAgents
- `uvicorn` - ASGI server for HTTP endpoints
- `click` - CLI framework
- `httpx` - Async HTTP client
- `python-dotenv` - Environment variable management
- `uagents` - uAgents framework
- `uagents-core` - Core uAgents functionality
- `langchain` - Language model integration
- `langchain-openai` - OpenAI integration for LangChain
- `langchain-core` - Core LangChain functionality


Now any A2A client can discover your uAgent and communicate with it using standard A2A protocol!
