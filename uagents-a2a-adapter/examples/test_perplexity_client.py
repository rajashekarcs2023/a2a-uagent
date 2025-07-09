#!/usr/bin/env python3
"""
Simplified A2A Client for Testing Perplexity Agent

This client sends research queries to the Perplexity agent running via the A2A adapter
with extended timeout handling for better reliability.
"""

import asyncio
import logging
from typing import Any
from uuid import uuid4
import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    MessageSendParams,
    SendMessageRequest,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimplifiedPerplexityClient:
    def __init__(self, base_url: str = "http://localhost:9001"):
        self.base_url = base_url
        self.httpx_client = None
        self.client = None
        self.agent_card = None
    
    async def __aenter__(self):
        # Create HTTP client with extended timeout for Perplexity queries
        self.httpx_client = httpx.AsyncClient(timeout=180.0)  # 3 minutes
        
        resolver = A2ACardResolver(
            httpx_client=self.httpx_client,
            base_url=self.base_url,
        )
        
        logger.info(f"🔍 Fetching agent card from: {self.base_url}/.well-known/agent.json")
        try:
            self.agent_card = await resolver.get_agent_card()
            logger.info(f"✅ Connected to agent: {self.agent_card.name}")
        except Exception as e:
            logger.error(f"❌ Failed to fetch agent card: {e}")
            raise
        
        self.client = A2AClient(
            httpx_client=self.httpx_client, 
            agent_card=self.agent_card
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.httpx_client:
            await self.httpx_client.aclose()
    
    async def send_message(self, text: str, context_id: str = None) -> dict:
        """Send a message to the Perplexity agent"""
        logger.info(f"📤 Sending query: {text}")
        
        if not context_id:
            context_id = f"perplexity-session-{uuid4().hex[:8]}"
        
        send_message_payload = {
            'message': {
                'role': 'user',
                'parts': [
                    {'kind': 'text', 'text': text}
                ],
                'messageId': uuid4().hex,
            },
            'contextId': context_id
        }
        
        request = SendMessageRequest(
            id=str(uuid4()), 
            params=MessageSendParams(**send_message_payload)
        )
        
        try:
            logger.info("⏳ Waiting for Perplexity response...")
            response = await self.client.send_message(request)
            logger.info("📨 Received response from Perplexity agent")
            return response.model_dump(mode='json', exclude_none=True)
        except asyncio.TimeoutError:
            logger.error("⏰ Request timed out - Perplexity agent may be processing complex query")
            return {"error": "timeout", "message": "Request timed out"}
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            return {"error": str(e)}

async def main():
    """Main function to test the Perplexity agent"""
    
    print("🔬 Simplified Perplexity A2A Client")
    print("=" * 50)
    
    # Test queries for the Perplexity agent
    test_queries = [
        "What are the latest developments in artificial intelligence?",
        "Explain quantum computing in simple terms",
        "What happened in tech news this week?",
        "Tell me about the current state of renewable energy"
    ]
    
    try:
        async with SimplifiedPerplexityClient() as client:
            print(f"🎯 Testing {len(test_queries)} research queries...\n")
            
            # Test each query
            context_id = f"test-session-{uuid4().hex[:8]}"
            
            for i, query in enumerate(test_queries, 1):
                print(f"📋 Query {i}/{len(test_queries)}: {query}")
                print("-" * 50)
                
                response = await client.send_message(query, context_id)
                
                if "error" in response:
                    print(f"❌ Error: {response['error']}")
                else:
                    # Extract the response text
                    try:
                        result = response.get('result', {})
                        status = result.get('status', {})
                        message = status.get('message', {})
                        parts = message.get('parts', [])
                        
                        if parts and len(parts) > 0:
                            response_text = parts[0].get('text', 'No response text')
                            print(f"✅ Response: {response_text[:200]}...")
                            if len(response_text) > 200:
                                print("    [Response truncated for display]")
                        else:
                            print("⚠️  No response text found in result")
                            
                    except Exception as e:
                        print(f"⚠️  Error parsing response: {e}")
                        print(f"Raw response: {response}")
                
                print("\n" + "="*50 + "\n")
                
                # Wait between queries to avoid overwhelming the agent
                if i < len(test_queries):
                    await asyncio.sleep(2)
            
            print("🎉 All test queries completed!")
            
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"❌ Client error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Perplexity A2A Client Test...")
    print("Make sure the A2A adapter is running on http://localhost:9001")
    print("Use: uagents-a2a --agent-address <perplexity-agent-address> --port 9001\n")
    
    asyncio.run(main())
