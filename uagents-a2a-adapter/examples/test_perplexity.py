#!/usr/bin/env python3
"""
Test: Perplexity Agent via A2A Adapter (Keeps Running)
"""

import time
from uagents_a2a_adapter import A2ARegisterTool

def main():
    """Start A2A adapter for Perplexity Agent and keep it running."""
    print("🚀 Starting Perplexity A2A Adapter")
    print("=" * 50)
    
    # Create adapter tool
    adapter = A2ARegisterTool()
    
    # Perplexity Agent configuration (using your corrected address)
    config = {
        "agent_address": "agent1qgzd0c60d4c5n37m4pzuclv5p9vwsftmfkznksec3drux8qnhmvuymsmshp",
        "name": "Perplexity Search Agent",
        "description": "AI-powered web search and research assistant",
        "host": "localhost", 
        "port": 10000,
        "skill_tags": ["search", "research", "web", "ai", "information"],
        "skill_examples": [
            "What are the latest developments in AI?",
            "Search for information about quantum computing",
            "Research recent news about space exploration"
        ]
    }
    
    print("🔧 Configuration:")
    print(f"   Agent Address: {config['agent_address']}")
    print(f"   Name: {config['name']}")
    print(f"   Port: {config['port']}")
    print("")
    
    try:
        # Start the adapter
        print("🚀 Starting A2A server...")
        result = adapter.invoke(config)
        
        if result.get("success"):
            print("✅ A2A Adapter Started Successfully!")
            print(f"🌐 Endpoint: {result['endpoint']}")
            print(f"📋 Agent: {result['agent_name']}")
            print("")
            print("🧪 Test with cURL:")
            print(f"""curl -X POST {result['endpoint']} \\
  -H "Content-Type: application/json" \\
  -d '{{
    "jsonrpc": "2.0",
    "id": "test-1",
    "method": "message/send",
    "params": {{
      "message": {{
        "role": "user",
        "parts": [{{"kind": "text", "text": "What are the latest AI developments?"}}],
        "messageId": "msg-1"
      }},
      "contextId": "research-session"
    }}
  }}'""")
            print("")
            print("🚀 Server is running! Press Ctrl+C to stop...")
            
            # Keep the script running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Stopping server...")
                
        else:
            print(f"❌ Failed to start: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
