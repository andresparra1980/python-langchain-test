"""
LLM-based topic similarity matching for intelligent domain selection.
"""

from typing import Optional, Dict, List
from langchain_openai import ChatOpenAI
from config import config


class TopicMatcher:
    """Uses LLM to determine if custom topics match existing domains"""

    def __init__(self):
        """Initialize the topic matcher with LLM"""
        # Initialize LLM based on provider
        if config.LLM_PROVIDER == "openrouter":
            self.llm = ChatOpenAI(
                model=config.LLM_MODEL,
                temperature=0.1,  # Low temperature for consistent matching
                api_key=config.OPENROUTER_API_KEY,
                base_url=config.OPENROUTER_BASE_URL,
            )
        else:  # Default to OpenAI
            self.llm = ChatOpenAI(
                model=config.LLM_MODEL,
                temperature=0.1,
                api_key=config.OPENAI_API_KEY,
            )

    def find_matching_domain(
        self,
        custom_topic: str,
        existing_domains: List[Dict[str, str]]
    ) -> Optional[str]:
        """
        Use LLM to determine if a custom topic matches an existing domain.

        Args:
            custom_topic: The custom topic name provided by user
            existing_domains: List of existing domains with name and description

        Returns:
            Name of matching domain, or None if no match
        """
        if not existing_domains:
            return None

        # Create prompt for LLM
        domains_list = "\n".join([
            f"- {d['name']}: {d['description']}"
            for d in existing_domains
        ])

        prompt = f"""You are a topic classification assistant. Determine if a custom research topic matches any existing research domains.

Custom topic: "{custom_topic}"

Existing domains:
{domains_list}

Task: Determine if the custom topic is broadly the same as any existing domain. Consider:
- Semantic similarity (e.g., "AI and Cybersecurity" matches "AI applied to infosec")
- Domain overlap (e.g., "Machine Learning" would match "AI/ML")
- Contextual equivalence (e.g., "Crypto assets" matches "Cryptocurrency")

IMPORTANT: Be flexible with matching. If the topics are in the same general area, consider them a match.

Respond with ONLY ONE of the following:
1. If there's a match: Return exactly "MATCH: <domain_name>" (use the exact domain name from the list)
2. If there's no match: Return exactly "NO_MATCH"

Examples:
- Custom topic: "AI and Cybersecurity" → MATCH: AI/ML
- Custom topic: "Crypto assets" → MATCH: cryptocurrency
- Custom topic: "Biotechnology" → NO_MATCH
- Custom topic: "Machine learning frameworks" → MATCH: AI/ML

Your response:"""

        try:
            response = self.llm.invoke(prompt)
            result = response.content.strip()

            # Parse response
            if result.startswith("MATCH:"):
                domain_name = result.replace("MATCH:", "").strip()
                # Verify the domain name is valid
                valid_names = [d["name"] for d in existing_domains]
                if domain_name in valid_names:
                    return domain_name

            return None

        except Exception as e:
            print(f"Error during LLM topic matching: {e}")
            return None


def find_similar_domain(
    custom_topic: str,
    existing_domains: List[Dict[str, str]]
) -> Optional[str]:
    """
    Convenience function to find matching domain.

    Args:
        custom_topic: Custom topic name
        existing_domains: List of existing domains

    Returns:
        Matching domain name or None
    """
    matcher = TopicMatcher()
    return matcher.find_matching_domain(custom_topic, existing_domains)
