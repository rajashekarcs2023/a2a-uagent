import logging
import asyncio
import threading
import time
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    InternalError,
    InvalidParamsError,
    Part,
    Task,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import (
    new_agent_text_message,
    new_task,
)
from a2a.utils.errors import ServerError

# Import uAgent for bridge communication
from uagents import Agent, Context, Model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Message models for uAgent communication
class QueryMessage(Model):
    query: str

class ResponseMessage(Model):
    response: str

class CurrencyAgentExecutor(AgentExecutor):
    """Currency Conversion AgentExecutor that bridges to uAgent."""
    
    def __init__(self):
        # Instead of: self.agent = CurrencyAgent()
        # Create bridge to your currency uAgent
        self.uagent_address = "agent1qv3yr66aw2qu3gzce5ckae84uj8ea5hua90q9mzwxcr9ghvtv0xeykme4dv"  # Your uAgent address
        self.response_cache = {}
        self.bridge_running = False
        self.pending_requests = {}
        
        # Create bridge agent with mailbox to communicate via Agentverse (same as currency uAgent)
        self.bridge_agent = Agent(
            name="a2a_bridge",
            port=8082,
            seed="a2a_bridge_seed",
            mailbox=True  # Enable mailbox so it can communicate with currency uAgent via Agentverse
        )
        self._setup_bridge()
        self._start_bridge()
        
    def _setup_bridge(self):
        """Setup bridge agent message handlers."""
        
        @self.bridge_agent.on_event("startup")
        async def bridge_startup(ctx: Context):
            self.bridge_running = True
            logger.info(f"A2A Bridge agent started with address: {ctx.agent.address}")
        
        @self.bridge_agent.on_message(model=ResponseMessage)
        async def handle_response(ctx: Context, sender: str, msg: ResponseMessage):
            # Use the sender address to match with pending request
            for request_id, request_info in list(self.pending_requests.items()):
                if request_info['target'] == sender:
                    self.response_cache[request_id] = msg.response
                    del self.pending_requests[request_id]
                    logger.info(f"Received response from currency uAgent: {msg.response[:100]}...")
                    break
        
        # Add a periodic task to process pending requests
        @self.bridge_agent.on_interval(period=0.1)
        async def process_pending_requests(ctx: Context):
            # Process any pending requests
            for request_id, request_info in list(self.pending_requests.items()):
                if not request_info.get('sent', False):
                    query_msg = QueryMessage(query=request_info['query'])
                    await ctx.send(self.uagent_address, query_msg)
                    self.pending_requests[request_id]['sent'] = True
                    self.pending_requests[request_id]['target'] = self.uagent_address
    
    def _start_bridge(self):
        """Start bridge agent in background thread."""
        def run_bridge():
            self.bridge_agent.run()
        
        thread = threading.Thread(target=run_bridge, daemon=True)
        thread.start()
        
        # Wait for bridge to start
        max_wait = 20
        wait_count = 0
        while not self.bridge_running and wait_count < max_wait:
            time.sleep(0.5)
            wait_count += 1
        
        if self.bridge_running:
            logger.info("✅ A2A Bridge to uAgent started successfully")
        else:
            logger.error("❌ Failed to start A2A bridge")

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        error = self._validate_request(context)
        if error:
            raise ServerError(error=InvalidParamsError())
        
        query = context.get_user_input()
        task = context.current_task
        
        if not task:
            task = new_task(context.message) # type: ignore
            await event_queue.enqueue_event(task)
        
        updater = TaskUpdater(event_queue, task.id, task.contextId)
        
        try:
            # Instead of: async for item in self.agent.stream(query, task.contextId):
            # Use bridge to communicate with uAgent:
            logger.info("Starting async iteration over uAgent bridge responses")
            async for item in self._stream_via_uagent(query, task.contextId):
                logger.info(f"Received item from bridge: {item}")
                is_task_complete = item['is_task_complete']
                require_user_input = item['require_user_input']
                
                if not is_task_complete and not require_user_input:
                    logger.info("Updating status to working")
                    await updater.update_status(
                        TaskState.working,
                        new_agent_text_message(
                            item['content'],
                            task.contextId,
                            task.id,
                        ),
                    )
                elif require_user_input:
                    logger.info("Updating status to input_required")
                    await updater.update_status(
                        TaskState.input_required,
                        new_agent_text_message(
                            item['content'],
                            task.contextId,
                            task.id,
                        ),
                        final=True,
                    )
                    break
                else:
                    logger.info("Adding artifact and completing task")
                    await updater.add_artifact(
                        [Part(root=TextPart(text=item['content']))],
                        name='conversion_result',
                    )
                    await updater.complete()
                    logger.info("Task completed successfully")
                    break
            logger.info("Finished async iteration")
        except Exception as e:
            logger.error(f'An error occurred while streaming the response: {e}')
            raise ServerError(error=InternalError()) from e

    async def _stream_via_uagent(self, query: str, context_id: str):
        """
        Bridge method that replaces self.agent.stream() 
        Same interface, but communicates with uAgent instead of direct LangGraph.
        """
        try:
            logger.info(f"Processing query via uAgent bridge: {query}")
            
            # Send working status first (same as original)
            yield {
                'is_task_complete': False,
                'require_user_input': False,
                'content': 'Looking up the exchange rates...'
            }
            
            # Create unique request ID
            request_id = f"req_{context_id}_{int(time.time())}"
            
            # Add request to pending queue
            self.pending_requests[request_id] = {
                'query': query,
                'sent': False,
                'target': None
            }
            
            # Wait for response with timeout
            timeout = 60  # 30 seconds
            wait_count = 0
            
            while request_id not in self.response_cache and wait_count < timeout:
                await asyncio.sleep(0.5)
                wait_count += 1
            
            if request_id in self.response_cache:
                response = self.response_cache.pop(request_id)
                logger.info(f"Successfully received response from currency uAgent")
                
                # Mimic the original agent's response format
                # Check if response indicates need for more input
                if any(phrase in response.lower() for phrase in [
                    "need more", "specify", "unclear", "provide more details", 
                    "which currency", "what amount"
                ]):
                    logger.info("Yielding input_required response")
                    yield {
                        'is_task_complete': False,
                        'require_user_input': True,
                        'content': response
                    }
                else:
                    # Successful completion (same format as original)
                    logger.info("Yielding completed response")
                    yield {
                        'is_task_complete': True,
                        'require_user_input': False,
                        'content': response
                    }
                logger.info("Response yielded successfully")
                return  # Explicitly return to end the generator
            else:
                # Timeout occurred
                logger.error("uAgent communication timed out")
                # Clean up pending request
                if request_id in self.pending_requests:
                    del self.pending_requests[request_id]
                yield {
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': 'Currency request timed out. Please try again.'
                }
                
        except Exception as e:
            logger.error(f"Error in uAgent bridge communication: {e}")
            yield {
                'is_task_complete': False,
                'require_user_input': True,
                'content': f'Error communicating with currency agent: {str(e)}'
            }

    def _validate_request(self, context: RequestContext) -> bool:
        return False

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise ServerError(error=UnsupportedOperationError())