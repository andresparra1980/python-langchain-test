"""
Topic management system for the research assistant.

Handles creation, switching, and management of research domains.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from src.memory.database import Database
from src.memory.models import ResearchDomain, ResearchTopic
from config import config


class TopicManager:
    """Manages research domains and topic switching"""

    # Default topic configurations
    PRESET_TOPICS = {
        "ai-ml": {
            "name": "AI/ML",
            "description": "Artificial Intelligence and Machine Learning development",
            "keywords": [
                "AI libraries",
                "ML frameworks",
                "LLM models",
                "vector databases",
                "transformers",
                "neural networks",
                "deep learning"
            ],
            "focus_areas": [
                "New libraries and frameworks",
                "Model releases",
                "Research papers",
                "Developer tools"
            ]
        },
        "cryptocurrency": {
            "name": "cryptocurrency",
            "description": "Cryptocurrency and blockchain technology",
            "keywords": [
                "blockchain",
                "DeFi",
                "smart contracts",
                "crypto protocols",
                "NFTs",
                "DAOs",
                "exchanges"
            ],
            "focus_areas": [
                "New protocols",
                "DeFi projects",
                "Regulations",
                "Exchange updates"
            ]
        },
        "web3": {
            "name": "web3",
            "description": "Web3 and decentralized technologies",
            "keywords": [
                "decentralized apps",
                "IPFS",
                "decentralized storage",
                "Web3 infrastructure",
                "dApps",
                "DAOs"
            ],
            "focus_areas": [
                "dApps",
                "Infrastructure",
                "Tools",
                "Communities"
            ]
        },
        "quantum-computing": {
            "name": "quantum-computing",
            "description": "Quantum computing and quantum algorithms",
            "keywords": [
                "quantum",
                "qubits",
                "quantum algorithms",
                "quantum hardware",
                "quantum supremacy",
                "quantum error correction"
            ],
            "focus_areas": [
                "Quantum hardware",
                "Quantum algorithms",
                "Quantum software",
                "Research breakthroughs"
            ]
        }
    }

    def __init__(self, database: Optional[Database] = None):
        """
        Initialize the topic manager.

        Args:
            database: Database instance (creates new one if not provided)
        """
        self.db = database or Database()
        self._current_domain_id: Optional[int] = None
        self._current_domain_name: Optional[str] = None

    def get_or_create_domain(self, domain_name: str) -> ResearchDomain:
        """
        Get an existing domain or create a new one.

        Args:
            domain_name: Name of the domain

        Returns:
            ResearchDomain object
        """
        with self.db.session_scope() as session:
            # Check if it's a preset key and get the actual name
            preset = self.PRESET_TOPICS.get(domain_name.lower())
            actual_name = preset["name"] if preset else domain_name

            # Try to find existing domain by actual name
            domain = session.query(ResearchDomain).filter(
                ResearchDomain.name == actual_name
            ).first()

            if domain:
                # Update last_used timestamp
                domain.last_used = datetime.utcnow()
                session.add(domain)
                session.expunge(domain)
                return domain

            # Create new domain
            if preset:
                # Create from preset
                domain = ResearchDomain(
                    name=preset["name"],
                    description=preset["description"],
                    keywords=preset["keywords"]
                )
            else:
                # Create custom domain
                domain = ResearchDomain(
                    name=domain_name,
                    description=f"Custom research domain: {domain_name}",
                    keywords=[]
                )

            session.add(domain)
            session.flush()
            session.expunge(domain)
            return domain

    def set_current_domain(self, domain_name: str) -> ResearchDomain:
        """
        Set the current research domain.

        Args:
            domain_name: Name of the domain to switch to

        Returns:
            ResearchDomain object
        """
        domain = self.get_or_create_domain(domain_name)
        self._current_domain_id = domain.id
        self._current_domain_name = domain.name
        return domain

    def get_current_domain(self) -> Optional[ResearchDomain]:
        """
        Get the current research domain.

        Returns:
            ResearchDomain object or None if not set
        """
        if not self._current_domain_id:
            return None

        with self.db.session_scope() as session:
            return session.query(ResearchDomain).filter(
                ResearchDomain.id == self._current_domain_id
            ).first()

    def list_domains(self) -> List[ResearchDomain]:
        """
        List all available research domains.

        Returns:
            List of ResearchDomain objects
        """
        with self.db.session_scope() as session:
            domains = session.query(ResearchDomain).order_by(
                ResearchDomain.last_used.desc()
            ).all()

            # Detach from session
            result = []
            for domain in domains:
                session.expunge(domain)
                result.append(domain)

            return result

    def get_domain_stats(self, domain_name: str) -> Dict[str, Any]:
        """
        Get statistics for a specific domain.

        Args:
            domain_name: Name of the domain

        Returns:
            Dictionary with domain statistics
        """
        with self.db.session_scope() as session:
            domain = session.query(ResearchDomain).filter(
                ResearchDomain.name == domain_name
            ).first()

            if not domain:
                return {
                    "exists": False,
                    "name": domain_name
                }

            # Count topics
            topic_count = session.query(ResearchTopic).filter(
                ResearchTopic.research_domain_id == domain.id
            ).count()

            # Get recent activity
            recent_topics = session.query(ResearchTopic).filter(
                ResearchTopic.research_domain_id == domain.id
            ).order_by(
                ResearchTopic.last_mentioned.desc()
            ).limit(5).all()

            return {
                "exists": True,
                "name": domain.name,
                "description": domain.description,
                "keywords": domain.keywords or [],
                "created_at": domain.created_at,
                "last_used": domain.last_used,
                "topic_count": topic_count,
                "recent_topics": [t.topic_name for t in recent_topics]
            }

    def delete_domain(self, domain_name: str, confirm: bool = False) -> bool:
        """
        Delete a research domain and all its topics.

        Args:
            domain_name: Name of the domain to delete
            confirm: Confirmation flag (must be True to actually delete)

        Returns:
            True if deleted, False otherwise
        """
        if not confirm:
            raise ValueError("Must set confirm=True to delete a domain")

        with self.db.session_scope() as session:
            domain = session.query(ResearchDomain).filter(
                ResearchDomain.name == domain_name
            ).first()

            if not domain:
                return False

            # Delete domain (cascades to topics)
            session.delete(domain)

            # Clear current domain if it was deleted
            if self._current_domain_id == domain.id:
                self._current_domain_id = None
                self._current_domain_name = None

            return True

    def create_custom_domain(
        self,
        name: str,
        description: str,
        keywords: List[str]
    ) -> ResearchDomain:
        """
        Create a custom research domain.

        Args:
            name: Domain name
            description: Domain description
            keywords: List of keywords

        Returns:
            ResearchDomain object
        """
        with self.db.session_scope() as session:
            # Check if exists
            existing = session.query(ResearchDomain).filter(
                ResearchDomain.name == name
            ).first()

            if existing:
                raise ValueError(f"Domain '{name}' already exists")

            domain = ResearchDomain(
                name=name,
                description=description,
                keywords=keywords
            )

            session.add(domain)
            session.flush()

            return domain

    def get_domain_prompt_context(self, domain_name: Optional[str] = None) -> Dict[str, str]:
        """
        Get prompt context for a specific domain.

        Args:
            domain_name: Name of the domain (uses current if not specified)

        Returns:
            Dictionary with prompt context
        """
        if not domain_name:
            domain_name = self._current_domain_name

        if not domain_name:
            # Default to AI/ML
            domain_name = "AI/ML"

        # Get preset or create generic context
        preset = None
        for key, preset_data in self.PRESET_TOPICS.items():
            if preset_data["name"].lower() == domain_name.lower():
                preset = preset_data
                break

        if preset:
            return {
                "domain": preset["name"],
                "description": preset["description"],
                "keywords": ", ".join(preset["keywords"]),
                "focus_areas": ", ".join(preset["focus_areas"])
            }
        else:
            # Get from database
            with self.db.session_scope() as session:
                domain = session.query(ResearchDomain).filter(
                    ResearchDomain.name == domain_name
                ).first()

                if domain:
                    return {
                        "domain": domain.name,
                        "description": domain.description or f"Research domain: {domain.name}",
                        "keywords": ", ".join(domain.keywords or []),
                        "focus_areas": "new developments, tools, and updates"
                    }

        # Fallback
        return {
            "domain": domain_name,
            "description": f"Research domain: {domain_name}",
            "keywords": "",
            "focus_areas": "new developments, tools, and updates"
        }


# Global topic manager instance
_topic_manager_instance: Optional[TopicManager] = None


def get_topic_manager() -> TopicManager:
    """
    Get or create the global topic manager instance.

    Returns:
        TopicManager instance
    """
    global _topic_manager_instance
    if _topic_manager_instance is None:
        _topic_manager_instance = TopicManager()
    return _topic_manager_instance


def reset_topic_manager():
    """Reset the global topic manager instance (useful for testing)"""
    global _topic_manager_instance
    _topic_manager_instance = None
