"""
Combined newsletter tool that retrieves findings and sends email in one step.
"""

from typing import List
from langchain.tools import Tool
from src.agent.tools.memory import MemoryTools
from src.agent.tools.email import EmailTools


class NewsletterTool:
    """Combined tool for newsletter generation and sending"""

    def __init__(self, current_domain_id: int = None):
        """
        Initialize newsletter tool.

        Args:
            current_domain_id: Current research domain ID
        """
        self.memory_tools = MemoryTools(current_domain_id=current_domain_id)
        self.email_tools = EmailTools()

    def send_research_newsletter(self, limit: str = "10") -> str:
        """
        Retrieve recent findings and send newsletter in one step.

        Args:
            limit: Number of topics to include (default: 10)

        Returns:
            Success or error message
        """
        # Get findings
        findings_json = self.memory_tools.get_recent_findings_for_newsletter(limit)

        # Send newsletter
        result = self.email_tools.send_newsletter(findings_json)

        return result

    def get_tool(self) -> Tool:
        """
        Get the combined newsletter tool.

        Returns:
            LangChain Tool object
        """
        return Tool(
            name="send_research_newsletter",
            func=self.send_research_newsletter,
            description=(
                "Send a newsletter email with recent research findings. "
                "Input: Number of topics to include as a string (e.g., '5' or '10'). "
                "This tool handles everything: retrieves recent findings from memory and sends them via email. "
                "Use this when the user requests a newsletter or email digest of research findings. "
                "Example inputs: '5', '10', '20'"
            )
        )


def create_newsletter_tool(current_domain_id: int = None) -> Tool:
    """
    Create the newsletter tool.

    Args:
        current_domain_id: Current research domain ID

    Returns:
        LangChain Tool object
    """
    newsletter_tool = NewsletterTool(current_domain_id=current_domain_id)
    return newsletter_tool.get_tool()
