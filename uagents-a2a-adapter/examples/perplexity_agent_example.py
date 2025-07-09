#!/usr/bin/env python3
"""
Example: Perplexity Agent via A2A Adapter

This example shows how to start an A2A adapter for the Perplexity Agent
and test it without authentication requirements.
"""

from uagents_a2a_adapter import A2ARegisterTool

def main():
    """Start A2A adapter for Perplexity Agent."""
    print("🔍 Starting Perplexity Agent A2A Adapter")
    print("=" * 50)
    
    # Create adapter tool
    adapter = A2ARegisterTool()
    
    # Perplexity Agent configuration
    perplexity_config = {
        "agent_address": "agent1qgzd0c60d4c5n37m4pzuclv5p9vwsftmfkznksec3drux8qnhmvuymsmshp",
        "name": "Perplexity Search Agent",
        "description": "AI-powered web search and research assistant with real-time information",
        "host": "localhost", 
        "port": 10000,
        "skill_tags": ["search", "research", "web", "ai", "information"],
        "skill_examples": [
            "What are the latest developments in AI?",
            "Search for recent news about space exploration",
            "Research renewable energy technologies",
            "What happened in the tech industry today?",
            "Find information about climate change solutions"
        ],
        "return_dict": True
    }
    
    print("🔧 Configuration:")
    print(f"   Agent Address: {perplexity_config['agent_address']}")
    print(f"   Name: {perplexity_config['name']}")
    print(f"   Port: {perplexity_config['port']}")
    print("")
    
    print("🎯 Features:")
    print("   ✅ No authentication required")
    print("   ✅ Real-time web search")
    print("   ✅ AI-powered research")
    print("   ✅ Cited sources and references")
    print("")
    
    try:
        # Start the adapter
        result = adapter.invoke(perplexity_config)
        
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
    "id": "perplexity-test-1",
    "method": "message/send",
    "params": {{
      "message": {{
        "role": "user",
        "parts": [{{"kind": "text", "text": "What are the latest developments in AI agents?"}}],
        "messageId": "msg-1"
      }},
      "contextId": "user-research-session"
    }}
  }}'""")
            print("")
            print("🚀 Ready for research queries!")
            
        else:
            print(f"❌ Failed to start adapter: {result.get('error')}")
            
    except KeyboardInterrupt:
        print("\n👋 Shutting down adapter...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
