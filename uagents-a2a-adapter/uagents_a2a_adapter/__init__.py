"""uAgents A2A Adapter Package."""

from .adapter import A2ARegisterTool
from .main import main
from .agentverse_agent_executor import AgentverseAgentExecutor

__version__ = "0.1.0"
__all__ = ["A2ARegisterTool", "main", "AgentverseAgentExecutor"]
