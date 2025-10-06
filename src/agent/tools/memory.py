from typing import Optional, List
from langchain.tools import Tool
from src.memory.service import MemoryService


class MemoryTools:
    """LangChain tools for querying and managing research memory"""
    
    def __init__(self):
        """Initialize memory tools"""
        self.memory_service = MemoryService()
    
    def check_memory(self, query: str) -> str:
        """
        Check if a topic has been researched before.
        
        Args:
            query: Topic name or search query
            
        Returns:
            String description of what was found in memory
        """
        # First try exact match
        topic = self.memory_service.get_topic_by_name(query, exact_match=True)
        
        if topic:
            days_ago = (self.memory_service.db.SessionLocal().query(
                self.memory_service.db.SessionLocal
            ).scalar())  # This is just placeholder
            
            from datetime import datetime
            days_ago = (datetime.utcnow() - topic.last_mentioned).days
            
            result = f"✓ Topic '{topic.topic_name}' was researched before.\n"
            result += f"Last mentioned: {days_ago} days ago\n"
            
            if topic.summary:
                result += f"Summary: {topic.summary}\n"
            
            if topic.sources:
                result += f"Sources ({len(topic.sources)}): {', '.join(topic.sources[:3])}"
                if len(topic.sources) > 3:
                    result += f" and {len(topic.sources) - 3} more"
                result += "\n"
            
            if topic.tags:
                result += f"Tags: {', '.join(topic.tags)}\n"
            
            return result
        
        # Try fuzzy search
        topics = self.memory_service.search_topics(query=query, limit=5)
        
        if topics:
            result = f"No exact match for '{query}', but found {len(topics)} related topics:\n\n"
            for i, t in enumerate(topics, 1):
                result += f"{i}. {t.topic_name} (last mentioned: "
                from datetime import datetime
                days = (datetime.utcnow() - t.last_mentioned).days
                result += f"{days} days ago)\n"
            return result
        
        return f"✗ No information found about '{query}' in memory. This appears to be a novel topic."
    
    def search_memory(self, query: str, tags: Optional[str] = None) -> str:
        """
        Search memory for topics matching query.
        
        Args:
            query: Search query
            tags: Comma-separated tags to filter by (optional)
            
        Returns:
            String with search results
        """
        tag_list = [t.strip() for t in tags.split(",")] if tags else None
        
        topics = self.memory_service.search_topics(
            query=query,
            tags=tag_list,
            limit=10
        )
        
        if not topics:
            return f"No topics found matching '{query}'"
        
        result = f"Found {len(topics)} topic(s) matching '{query}':\n\n"
        
        for i, topic in enumerate(topics, 1):
            from datetime import datetime
            days_ago = (datetime.utcnow() - topic.last_mentioned).days
            
            result += f"{i}. {topic.topic_name}\n"
            result += f"   Last mentioned: {days_ago} days ago\n"
            
            if topic.summary:
                # Truncate long summaries
                summary = topic.summary[:200]
                if len(topic.summary) > 200:
                    summary += "..."
                result += f"   Summary: {summary}\n"
            
            if topic.tags:
                result += f"   Tags: {', '.join(topic.tags)}\n"
            
            result += "\n"
        
        return result
    
    def check_novelty(self, topic_name: str) -> str:
        """
        Check if a topic is novel (not researched recently).
        
        Args:
            topic_name: Topic name to check
            
        Returns:
            String indicating whether topic is novel
        """
        is_novel = self.memory_service.is_novel(topic_name, days_threshold=7)
        
        if is_novel:
            topic = self.memory_service.get_topic_by_name(topic_name, exact_match=False)
            if topic:
                from datetime import datetime
                days_ago = (datetime.utcnow() - topic.last_mentioned).days
                return (
                    f"✓ Topic '{topic_name}' is considered NOVEL.\n"
                    f"Last researched {days_ago} days ago (threshold: 7 days).\n"
                    f"You can provide new information about this topic."
                )
            else:
                return (
                    f"✓ Topic '{topic_name}' is NOVEL - never researched before.\n"
                    f"Feel free to research and share information about it."
                )
        else:
            topic = self.memory_service.get_topic_by_name(topic_name, exact_match=False)
            from datetime import datetime
            days_ago = (datetime.utcnow() - topic.last_mentioned).days
            return (
                f"✗ Topic '{topic_name}' is NOT novel.\n"
                f"Last mentioned {days_ago} days ago (threshold: 7 days).\n"
                f"Avoid repeating the same information unless specifically requested."
            )
    
    def get_memory_stats(self, _: str = "") -> str:
        """
        Get statistics about the memory system.
        
        Args:
            _: Unused parameter (for LangChain tool compatibility)
            
        Returns:
            String with memory statistics
        """
        stats = self.memory_service.get_stats()
        
        result = "Memory System Statistics:\n\n"
        result += f"Total topics researched: {stats['total_topics']}\n"
        result += f"Topics mentioned in last 7 days: {stats['recent_topics_7days']}\n"
        result += f"Database: {stats['database_url']}\n"
        
        return result
    
    def get_tools(self) -> List[Tool]:
        """
        Get LangChain tools for memory operations.
        
        Returns:
            List of LangChain Tool objects
        """
        return [
            Tool(
                name="check_memory",
                func=self.check_memory,
                description=(
                    "Check if a topic has been researched before. "
                    "Use this BEFORE researching a new topic to avoid repetition. "
                    "Input should be the topic name or query string. "
                    "Returns information about previous research including summary, sources, and when it was last mentioned."
                )
            ),
            Tool(
                name="search_memory",
                func=self.search_memory,
                description=(
                    "Search memory for topics matching a query. "
                    "Useful for finding related topics or browsing research history. "
                    "Input should be a search query string. "
                    "Returns a list of matching topics with summaries and metadata."
                )
            ),
            Tool(
                name="check_novelty",
                func=self.check_novelty,
                description=(
                    "Check if a topic is novel (not researched in the last 7 days). "
                    "Use this to determine if you should provide information about a topic. "
                    "Input should be the topic name. "
                    "Returns whether the topic is novel or has been recently covered."
                )
            ),
            Tool(
                name="memory_stats",
                func=self.get_memory_stats,
                description=(
                    "Get statistics about the memory system. "
                    "Shows total topics, recent activity, and database info. "
                    "No input required - just call it to get stats."
                )
            ),
        ]


def create_memory_tools() -> List[Tool]:
    """
    Convenience function to create memory tools.
    
    Returns:
        List of LangChain Tool objects for memory operations
    """
    memory_tools = MemoryTools()
    return memory_tools.get_tools()
