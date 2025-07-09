import logging
import os
import sys
import click
import httpx
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryPushNotifier, InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from dotenv import load_dotenv

# Import the generic agent executor
from .agentverse_agent_executor import AgentverseAgentExecutor

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MissingParameterError(Exception):
    """Exception for missing required parameters."""

@click.command()
@click.option('--host', 'host', default='localhost', help='Host to bind the server to')
@click.option('--port', 'port', default=10000, help='Port to bind the server to')
@click.option('--agent-address', 'agent_address', required=True, help='Agentverse agent address to bridge to')
@click.option('--agent-name', 'agent_name', default='Agentverse Agent', help='Name for the A2A agent')
@click.option('--agent-description', 'agent_description', default='Agent bridged from Agentverse', help='Description for the A2A agent')
@click.option('--skill-tags', 'skill_tags', default='general,assistance', help='Comma-separated skill tags')
@click.option('--skill-examples', 'skill_examples', default='Help me with my query', help='Comma-separated skill examples')
def main(host, port, agent_address, agent_name, agent_description, skill_tags, skill_examples):
    """Starts the Agentverse Bridge A2A server."""
    try:
        logger.info(f"Starting A2A server bridged to Agentverse agent: {agent_address}")
        
        # Parse comma-separated values
        tags = [tag.strip() for tag in skill_tags.split(',')]
        examples = [example.strip() for example in skill_examples.split(',')]
        
        # Create agent capabilities
        capabilities = AgentCapabilities(streaming=True, pushNotifications=True)
        
        # Create agent skill
        skill = AgentSkill(
            id='agentverse_bridge',
            name=f'{agent_name} Bridge',
            description=agent_description,
            tags=tags,
            examples=examples,
        )

        # Create agent card
        agent_card = AgentCard(
            name=agent_name,
            description=agent_description,
            url=f'http://{host}:{port}/',
            version='1.0.0',
            defaultInputModes=['text', 'text/plain'],
            defaultOutputModes=['text', 'text/plain'],
            capabilities=capabilities,
            skills=[skill],
        )

        # Create the bridge executor with the target agent address
        bridge_executor = AgentverseAgentExecutor(
            target_agent_address=agent_address,
            bridge_name="a2a_agentverse_bridge",
            bridge_port=8082
        )

        # Create request handler
        httpx_client = httpx.AsyncClient()
        request_handler = DefaultRequestHandler(
            agent_executor=bridge_executor,
            task_store=InMemoryTaskStore(),
            push_notifier=InMemoryPushNotifier(httpx_client),
        )

        # Create and run server
        server = A2AStarletteApplication(
            agent_card=agent_card, 
            http_handler=request_handler
        )

        logger.info(f"🚀 A2A server starting on {host}:{port}")
        logger.info(f"🔗 Bridging to Agentverse agent: {agent_address}")
        logger.info(f"📋 Agent name: {agent_name}")
        logger.info(f"🏷️  Tags: {', '.join(tags)}")
        
        uvicorn.run(server.build(), host=host, port=port)

    except MissingParameterError as e:
        logger.error(f'Error: {e}')
        sys.exit(1)
    except Exception as e:
        logger.error(f'An error occurred during server startup: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()