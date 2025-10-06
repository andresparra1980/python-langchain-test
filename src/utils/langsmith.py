import os
from typing import Optional
from langsmith import Client
from config import config


def setup_langsmith_tracing() -> Optional[Client]:
    """
    Configure LangSmith tracing for the agent.
    
    Sets up environment variables and returns a LangSmith client if configured.
    Returns None if LangSmith is not configured or disabled.
    """
    if not config.LANGSMITH_TRACING:
        return None
    
    if not config.LANGSMITH_API_KEY:
        print("Warning: LangSmith tracing enabled but LANGSMITH_API_KEY not set")
        return None
    
    # Set environment variables for LangChain's automatic tracing
    os.environ["LANGSMITH_TRACING_V2"] = "true"
    os.environ["LANGSMITH_API_KEY"] = config.LANGSMITH_API_KEY
    os.environ["LANGSMITH_PROJECT"] = config.LANGSMITH_PROJECT
    
    # Create and return LangSmith client
    client = Client(
        api_key=config.LANGSMITH_API_KEY,
        project_name=config.LANGSMITH_PROJECT
    )
    
    print(f"✓ LangSmith tracing enabled for project: {config.LANGSMITH_PROJECT}")
    return client


def disable_langsmith_tracing():
    """Disable LangSmith tracing"""
    os.environ["LANGSMITH_TRACING_V2"] = "false"
    print("✓ LangSmith tracing disabled")


def get_langsmith_url(run_id: str) -> str:
    """
    Generate LangSmith URL for a specific run.
    
    Args:
        run_id: The run ID from LangSmith
        
    Returns:
        URL to view the run in LangSmith
    """
    project_name = config.LANGSMITH_PROJECT.replace(" ", "-")
    return f"https://smith.langchain.com/o/default/projects/p/{project_name}/r/{run_id}"
