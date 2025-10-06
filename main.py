#!/usr/bin/env python3
"""
AI Research Assistant Agent - Main Entry Point

This script starts the AI research assistant with the selected input adapter (CLI or Telegram).
"""

import sys
import argparse
from typing import Optional

from config import config
from src.agent.core import ResearchAgent
from src.agent.tools.search import create_search_tools
from src.agent.tools.email import create_email_tools
from src.agent.tools.memory import MemoryTools
from src.adapters.cli import CLIAdapter
from src.adapters.telegram import TelegramAdapter
from src.topic.manager import TopicManager
from src.topic.selector import select_topic, display_topic_stats


def create_agent(verbose: bool = True) -> ResearchAgent:
    """
    Create and configure the research agent with all tools.

    Args:
        verbose: Whether to enable verbose output

    Returns:
        Configured ResearchAgent instance
    """
    print("🔧 Initializing agent...")

    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)

    # Select research topic
    topic_name = select_topic(config.RESEARCH_TOPIC)

    # Initialize topic manager and set current domain
    topic_manager = TopicManager()
    current_domain = topic_manager.set_current_domain(topic_name)

    # Display topic stats
    display_topic_stats(topic_manager, topic_name)

    # Create all tool sets with topic filtering
    try:
        search_tools = create_search_tools()
        print(f"  ✓ Loaded {len(search_tools)} search tools")

        email_tools = create_email_tools()
        print(f"  ✓ Loaded {len(email_tools)} email tools")

        # Create memory tools with current domain
        memory_tools_instance = MemoryTools(current_domain_id=current_domain.id)
        memory_tools = memory_tools_instance.get_tools()
        print(f"  ✓ Loaded {len(memory_tools)} memory tools")

        # Combine all tools
        all_tools = search_tools + email_tools + memory_tools
        print(f"  ✓ Total tools available: {len(all_tools)}")

    except Exception as e:
        print(f"❌ Error loading tools: {e}")
        sys.exit(1)

    # Create agent with topic manager
    try:
        agent = ResearchAgent(
            tools=all_tools,
            verbose=verbose,
            use_memory=True,
            enable_langsmith=config.LANGSMITH_TRACING,
            topic_manager=topic_manager
        )
        print("  ✓ Agent initialized successfully")
        return agent

    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        sys.exit(1)


def start_cli(agent: ResearchAgent) -> None:
    """
    Start the CLI adapter.

    Args:
        agent: The configured ResearchAgent instance
    """
    print("\n🚀 Starting CLI interface...\n")

    cli_adapter = CLIAdapter(agent_core=agent)
    cli_adapter.start()


def start_telegram(agent: ResearchAgent, bot_token: Optional[str] = None) -> None:
    """
    Start the Telegram bot adapter.

    Args:
        agent: The configured ResearchAgent instance
        bot_token: Optional bot token (uses config if not provided)
    """
    print("\n🚀 Starting Telegram bot...\n")

    try:
        telegram_adapter = TelegramAdapter(agent_core=agent, bot_token=bot_token)
        telegram_adapter.start()
    except ValueError as e:
        print(f"❌ {e}")
        print("\nPlease set TELEGRAM_BOT_TOKEN in your .env file or provide it via command line.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error running Telegram bot: {e}")
        sys.exit(1)


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="AI Research Assistant Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Start CLI interface (default)
  %(prog)s --telegram         # Start Telegram bot
  %(prog)s --quiet            # Start CLI with minimal output
  %(prog)s --telegram --token YOUR_BOT_TOKEN  # Start Telegram with custom token
        """
    )

    parser.add_argument(
        "--telegram",
        action="store_true",
        help="Start Telegram bot instead of CLI"
    )

    parser.add_argument(
        "--token",
        type=str,
        help="Telegram bot token (only used with --telegram)"
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce agent verbosity"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="AI Research Assistant v0.1.0"
    )

    args = parser.parse_args()

    # Display banner
    print("""
╔════════════════════════════════════════════════════════════╗
║         AI Research Assistant Agent                       ║
║         Powered by LangChain & LangSmith                  ║
╚════════════════════════════════════════════════════════════╝
    """)

    # Create agent
    agent = create_agent(verbose=not args.quiet)

    # Start appropriate adapter
    if args.telegram:
        start_telegram(agent, bot_token=args.token)
    else:
        start_cli(agent)


if __name__ == "__main__":
    main()
