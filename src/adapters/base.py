from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class InputAdapter(ABC):
    """
    Abstract base class for input adapters.

    Input adapters provide a modular interface for receiving user input
    from different channels (CLI, Telegram, WhatsApp, web) and sending
    responses back through the same channel.

    Each adapter implementation should handle channel-specific details like
    message formatting, session management, and authentication while providing
    a consistent interface for the agent core.
    """

    def __init__(self, agent_core=None):
        """
        Initialize the input adapter.

        Args:
            agent_core: The agent core instance to process messages
        """
        self.agent_core = agent_core
        self.session_data: Dict[str, Any] = {}

    @abstractmethod
    def start(self) -> None:
        """
        Start the adapter and begin listening for input.

        This method should implement the main loop or event listener
        for the specific input channel.
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        Stop the adapter and clean up resources.

        This method should gracefully shut down the adapter and
        release any resources (connections, file handles, etc.).
        """
        pass

    @abstractmethod
    def receive_message(self) -> Optional[str]:
        """
        Receive a message from the input channel.

        Returns:
            The received message as a string, or None if no message is available
        """
        pass

    @abstractmethod
    def send_message(self, message: str) -> bool:
        """
        Send a message through the output channel.

        Args:
            message: The message to send

        Returns:
            True if the message was sent successfully, False otherwise
        """
        pass

    def format_response(self, response: str) -> str:
        """
        Format a response for the specific channel.

        This method can be overridden by subclasses to apply channel-specific
        formatting (e.g., Markdown for Telegram, plain text for CLI).

        Args:
            response: The raw response from the agent

        Returns:
            The formatted response
        """
        return response

    def process_message(self, message: str) -> Optional[str]:
        """
        Process a message through the agent core and get a response.

        Args:
            message: The user's message

        Returns:
            The agent's response, or None if processing failed
        """
        if not self.agent_core:
            return "Error: No agent core configured"

        try:
            # Reset tool call counter for this message
            # Each user message gets a fresh limit
            if hasattr(self.agent_core, 'reset_tool_call_count'):
                self.agent_core.reset_tool_call_count()

            # Process message through agent
            result = self.agent_core.run(message)

            # Extract output from result dictionary
            if isinstance(result, dict):
                response = result.get("output", str(result))
            else:
                response = str(result)

            # Format response for this channel
            formatted_response = self.format_response(response)

            return formatted_response

        except Exception as e:
            error_message = f"Error processing message: {str(e)}"
            return self.format_response(error_message)

    def get_session_data(self, key: str, default=None) -> Any:
        """
        Get session data for this adapter.

        Args:
            key: The session data key
            default: Default value if key doesn't exist

        Returns:
            The session data value
        """
        return self.session_data.get(key, default)

    def set_session_data(self, key: str, value: Any) -> None:
        """
        Set session data for this adapter.

        Args:
            key: The session data key
            value: The value to store
        """
        self.session_data[key] = value

    def clear_session_data(self) -> None:
        """Clear all session data."""
        self.session_data.clear()
