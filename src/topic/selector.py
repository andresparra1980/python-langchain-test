"""
Topic selection UI for startup.

Handles interactive topic selection when RESEARCH_TOPIC is not configured.
"""

from typing import Optional
from src.topic.manager import TopicManager


def display_topic_menu():
    """Display the topic selection menu"""
    print("\n" + "="*60)
    print("     Research Assistant - Topic Selection")
    print("="*60 + "\n")
    print("What would you like to research?\n")
    print("  1. AI/ML Development (default)")
    print("  2. Cryptocurrency & Blockchain")
    print("  3. Web3 & Decentralized Tech")
    print("  4. Quantum Computing")
    print("  5. Custom topic (you specify)\n")


def get_user_choice() -> str:
    """
    Get user's topic choice.

    Returns:
        Topic name selected by user
    """
    while True:
        try:
            choice = input("Your choice (1-5): ").strip()

            if choice == "1":
                return "ai-ml"
            elif choice == "2":
                return "cryptocurrency"
            elif choice == "3":
                return "web3"
            elif choice == "4":
                return "quantum-computing"
            elif choice == "5":
                custom_topic = input("\nEnter your custom topic name: ").strip()
                if custom_topic:
                    # Check for similar existing domains using LLM
                    print(f"\n🔍 Checking if '{custom_topic}' matches any existing domains...")

                    topic_manager = TopicManager()
                    matched_domain_name = None

                    try:
                        from src.topic.matcher import find_similar_domain

                        existing_domains = topic_manager.list_domains()

                        if existing_domains:
                            # Prepare domain list for LLM matching
                            existing_domains_list = [
                                {"name": d.name, "description": d.description or ""}
                                for d in existing_domains
                            ]

                            # Use LLM to find similar domain
                            matched_domain_name = find_similar_domain(custom_topic, existing_domains_list)

                            if matched_domain_name:
                                print(f"\n💡 This topic seems similar to existing domain: '{matched_domain_name}'")
                                use_existing = input("Would you like to use that instead? (y/n): ").strip().lower()

                                if use_existing == 'y':
                                    print(f"\n✓ Using existing domain: {matched_domain_name}")
                                    return matched_domain_name
                                else:
                                    print("\n📝 Creating new custom topic instead...")
                            else:
                                print("\n✓ No similar domains found. Creating new topic.")
                        else:
                            print("\n📝 No existing domains to compare.")

                    except Exception as e:
                        print(f"\n⚠️  Could not check for similar domains: {str(e)}")
                        print("Proceeding with custom topic creation...\n")

                    # Ask for optional description
                    description = input("\nBrief description (optional): ").strip()
                    keywords_input = input("Keywords (comma-separated, optional): ").strip()

                    keywords = []
                    if keywords_input:
                        keywords = [k.strip() for k in keywords_input.split(",")]

                    # Create custom topic
                    try:
                        topic_manager.create_custom_domain(
                            name=custom_topic,
                            description=description or f"Custom research domain: {custom_topic}",
                            keywords=keywords
                        )
                        print(f"\n✓ Created custom topic: {custom_topic}")
                    except ValueError as e:
                        # Topic already exists
                        print(f"\n✓ Using existing topic: {custom_topic}")

                    return custom_topic
                else:
                    print("Please enter a topic name.")
            else:
                print("Invalid choice. Please enter 1-5.")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            exit(0)
        except Exception as e:
            print(f"Error: {e}")


def select_topic(configured_topic: Optional[str] = None) -> str:
    """
    Select research topic, either from config or interactively.

    Args:
        configured_topic: Topic from config (RESEARCH_TOPIC env var)

    Returns:
        Selected topic name
    """
    # If topic is configured, use it
    if configured_topic:
        print(f"\n✓ Using configured topic: {configured_topic}")
        return configured_topic

    # Otherwise, prompt user
    display_topic_menu()
    topic = get_user_choice()

    print(f"\n✓ Selected topic: {topic}\n")
    return topic


def display_topic_stats(topic_manager: TopicManager, topic_name: str):
    """
    Display statistics for the selected topic.

    Args:
        topic_manager: TopicManager instance
        topic_name: Name of the topic
    """
    stats = topic_manager.get_domain_stats(topic_name)

    if not stats["exists"]:
        print(f"✓ New research domain - no previous data")
        return

    print(f"✓ Domain: {stats['name']}")
    if stats.get("description"):
        print(f"  Description: {stats['description']}")
    print(f"  Topics researched: {stats['topic_count']}")

    if stats.get("recent_topics"):
        print(f"  Recent topics: {', '.join(stats['recent_topics'][:3])}")
        if len(stats['recent_topics']) > 3:
            print(f"                 ...and {len(stats['recent_topics']) - 3} more")
    print()
