import sys
from typing import Optional
from src.adapters.base import InputAdapter


class CLIAdapter(InputAdapter):
    """
    Command-line interface adapter for terminal-based interaction.

    Provides a simple REPL (Read-Eval-Print Loop) for interacting with the
    agent through a terminal. Supports colored output and formatted responses.
    """

    def __init__(self, agent_core=None, prompt: str = "You: "):
        """
        Initialize the CLI adapter.

        Args:
            agent_core: The agent core instance to process messages
            prompt: The input prompt to display
        """
        super().__init__(agent_core)
        self.prompt = prompt
        self.running = False
        self.use_colors = self._check_color_support()

    def _check_color_support(self) -> bool:
        """
        Check if the terminal supports ANSI colors.

        Returns:
            True if colors are supported, False otherwise
        """
        # Check if stdout is a terminal and not redirected
        if not sys.stdout.isatty():
            return False

        # Check TERM environment variable
        import os
        term = os.getenv("TERM", "").lower()
        return "color" in term or "ansi" in term or "xterm" in term

    def _colorize(self, text: str, color: str) -> str:
        """
        Apply ANSI color codes to text if colors are supported.

        Args:
            text: The text to colorize
            color: Color name (blue, green, yellow, red, cyan, magenta)

        Returns:
            Colorized text or plain text if colors not supported
        """
        if not self.use_colors:
            return text

        colors = {
            "blue": "\033[94m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "red": "\033[91m",
            "cyan": "\033[96m",
            "magenta": "\033[95m",
            "bold": "\033[1m",
            "reset": "\033[0m",
        }

        color_code = colors.get(color, "")
        reset_code = colors["reset"]

        return f"{color_code}{text}{reset_code}"

    def start(self) -> None:
        """
        Start the CLI adapter and begin the interaction loop.

        This method starts a REPL that continuously reads user input,
        processes it through the agent, and displays responses.
        """
        self.running = True

        # Display welcome message
        self._display_welcome()

        try:
            while self.running:
                # Get user input
                try:
                    user_input = input(self._colorize(self.prompt, "cyan"))
                except EOFError:
                    # Handle Ctrl+D
                    print()
                    break
                except KeyboardInterrupt:
                    # Handle Ctrl+C
                    print()
                    break

                # Skip empty input
                if not user_input.strip():
                    continue

                # Check for exit commands
                if user_input.strip().lower() in ["exit", "quit", "bye"]:
                    self._display_goodbye()
                    break

                # Check for help command
                if user_input.strip().lower() in ["help", "?"]:
                    self._display_help()
                    continue

                # Check for clear command
                if user_input.strip().lower() == "clear":
                    self.clear_session_data()
                    print(self._colorize("✓ Session cleared", "green"))
                    continue

                # Check for topic commands
                if user_input.strip().lower().startswith("/topic"):
                    self._handle_topic_command(user_input.strip())
                    continue

                # Check for memory commands
                if user_input.strip().lower().startswith("/memory"):
                    self._handle_memory_command(user_input.strip())
                    continue

                # Process message through agent
                response = self.process_message(user_input)

                # Display response
                if response:
                    self.send_message(response)

        except Exception as e:
            print(self._colorize(f"\n✗ Error: {str(e)}", "red"))
        finally:
            self.stop()

    def stop(self) -> None:
        """
        Stop the CLI adapter.

        Performs cleanup and sets the running flag to False.
        """
        self.running = False

    def receive_message(self) -> Optional[str]:
        """
        Receive a message from the CLI.

        This method is implemented for interface compatibility but not
        used in the main loop. Use the start() method instead.

        Returns:
            User input or None if cancelled
        """
        try:
            return input(self._colorize(self.prompt, "cyan"))
        except (EOFError, KeyboardInterrupt):
            return None

    def send_message(self, message: str) -> bool:
        """
        Send a message to the CLI output.

        Args:
            message: The message to display

        Returns:
            True if message was displayed successfully
        """
        try:
            # Format the message with agent prefix
            formatted = self._colorize("Agent: ", "blue") + message
            print(formatted)
            print()  # Empty line for readability
            return True
        except Exception as e:
            print(self._colorize(f"Error displaying message: {str(e)}", "red"))
            return False

    def format_response(self, response: str) -> str:
        """
        Format a response for CLI display.

        Args:
            response: The raw response from the agent

        Returns:
            Formatted response (currently just returns the original)
        """
        # For CLI, we keep formatting simple
        # Could add markdown rendering here if desired
        return response

    def _display_welcome(self) -> None:
        """Display a welcome message when the CLI starts."""
        welcome = """
╔════════════════════════════════════════════════════════════╗
║         AI Research Assistant - CLI Interface             ║
╚════════════════════════════════════════════════════════════╝

Welcome! I'm your AI research assistant. I can help you:
  • Research trending AI topics and technologies
  • Search for papers, libraries, and frameworks
  • Remember what we've discussed to avoid repetition
  • Send newsletter summaries via email

Type 'help' for commands, or just start chatting!
Type 'exit' to quit.

"""
        print(self._colorize(welcome, "cyan"))

    def _display_goodbye(self) -> None:
        """Display a goodbye message when exiting."""
        goodbye = "\n" + self._colorize("Goodbye! Happy researching! 👋", "green") + "\n"
        print(goodbye)

    def _display_help(self) -> None:
        """Display help information."""
        help_text = """
Available commands:
  help, ?           - Show this help message
  clear             - Clear conversation history
  /topic            - Show current research topic
  /topic list       - List all available topics
  /topic set <name> - Switch to a different topic
  /memory clear     - Clear all memory for current topic
  /memory stats     - Show memory statistics
  exit, quit        - Exit the application

You can ask me to:
  • "Research new Python AI libraries"
  • "Search for papers about transformers"
  • "What did we discuss about LangChain?"
  • "Send me a newsletter with recent findings"
  • And more!

"""
        print(self._colorize(help_text, "yellow"))

    def _handle_topic_command(self, command: str) -> None:
        """
        Handle topic management commands.

        Args:
            command: The topic command string
        """
        from src.topic.manager import get_topic_manager

        parts = command.split()
        topic_manager = get_topic_manager()

        if len(parts) == 1:
            # Show current topic
            current_domain = topic_manager.get_current_domain()
            if current_domain:
                print(self._colorize(f"\nCurrent topic: {current_domain.name}", "green"))
                stats = topic_manager.get_domain_stats(current_domain.name)
                print(f"Topics researched: {stats['topic_count']}")
                if stats.get('recent_topics'):
                    print(f"Recent: {', '.join(stats['recent_topics'][:3])}\n")
            else:
                print(self._colorize("\nNo topic currently selected", "yellow"))

        elif len(parts) >= 2 and parts[1].lower() == "list":
            # List all topics
            domains = topic_manager.list_domains()
            if domains:
                print(self._colorize("\nAvailable research topics:", "green"))
                for i, domain in enumerate(domains, 1):
                    stats = topic_manager.get_domain_stats(domain.name)
                    current_marker = " (current)" if domain.id == topic_manager._current_domain_id else ""
                    print(f"  {i}. {domain.name}{current_marker} - {stats['topic_count']} topics")
                print()
            else:
                print(self._colorize("\nNo topics available", "yellow"))

        elif len(parts) >= 3 and parts[1].lower() == "set":
            # Switch topic
            new_topic = " ".join(parts[2:])
            try:
                # Confirm switch
                print(self._colorize(f"\n⚠️  Switching to topic: {new_topic}", "yellow"))
                print("This will change your research context.")
                confirm = input("Continue? (y/n): ").strip().lower()

                if confirm == "y":
                    # Note: This requires restarting the agent to update memory tools
                    print(self._colorize("\n✗ Topic switching requires restarting the agent.", "red"))
                    print("Please restart the application with RESEARCH_TOPIC set to:", new_topic)
                    print("Or add it to your .env file.\n")
                else:
                    print(self._colorize("\nCancelled", "yellow"))
            except Exception as e:
                print(self._colorize(f"\n✗ Error: {str(e)}\n", "red"))

        else:
            print(self._colorize("\nInvalid topic command. Usage:", "yellow"))
            print("  /topic            - Show current topic")
            print("  /topic list       - List all topics")
            print("  /topic set <name> - Switch topic (requires restart)\n")

    def _handle_memory_command(self, command: str) -> None:
        """
        Handle memory management commands.

        Args:
            command: The memory command string
        """
        from src.topic.manager import get_topic_manager
        from src.memory.service import MemoryService

        parts = command.split()
        topic_manager = get_topic_manager()
        current_domain = topic_manager.get_current_domain()

        if not current_domain:
            print(self._colorize("\n✗ No topic selected\n", "red"))
            return

        memory_service = MemoryService(current_domain_id=current_domain.id)

        if len(parts) == 1:
            # Show memory help
            print(self._colorize("\nMemory commands:", "yellow"))
            print("  /memory clear  - Clear all topics for current domain")
            print("  /memory stats  - Show memory statistics\n")

        elif len(parts) >= 2 and parts[1].lower() == "clear":
            # Clear memory for current domain
            try:
                print(self._colorize(f"\n⚠️  Warning: This will delete ALL {current_domain.name} research topics from memory.", "yellow"))
                confirm = input("Are you sure? Type 'yes' to confirm: ").strip().lower()

                if confirm == "yes":
                    # Get all topics for current domain and delete them
                    topics = memory_service.search_topics(query="", limit=1000)
                    count = len(topics)

                    for topic in topics:
                        memory_service.delete_topic(topic.id)

                    print(self._colorize(f"\n✓ Cleared {count} topics from {current_domain.name} memory\n", "green"))
                else:
                    print(self._colorize("\nCancelled\n", "yellow"))

            except Exception as e:
                print(self._colorize(f"\n✗ Error clearing memory: {str(e)}\n", "red"))

        elif len(parts) >= 2 and parts[1].lower() == "stats":
            # Show memory statistics
            try:
                stats = memory_service.get_stats()
                print(self._colorize(f"\nMemory Statistics for {current_domain.name}:", "green"))
                print(f"  Total topics: {stats['total_topics']}")
                print(f"  Recent (7 days): {stats['recent_topics_7days']}\n")
            except Exception as e:
                print(self._colorize(f"\n✗ Error getting stats: {str(e)}\n", "red"))

        else:
            print(self._colorize("\nInvalid memory command. Usage:", "yellow"))
            print("  /memory clear  - Clear all topics")
            print("  /memory stats  - Show statistics\n")
