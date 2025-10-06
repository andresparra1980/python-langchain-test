from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from src.memory.models import ResearchTopic
from src.memory.database import get_database


class MemoryService:
    """Service layer for managing research topic memory"""

    def __init__(self, current_domain_id: Optional[int] = None):
        """
        Initialize the memory service.

        Args:
            current_domain_id: Current research domain ID for filtering
        """
        self.db = get_database()
        self.current_domain_id = current_domain_id
    
    def store_topic(
        self,
        topic_name: str,
        summary: str = None,
        sources: List[str] = None,
        tags: List[str] = None,
        session: Session = None
    ) -> ResearchTopic:
        """
        Store a new research topic in memory.

        Args:
            topic_name: Name of the topic
            summary: Summary of research findings
            sources: List of source URLs
            tags: List of tags/categories
            session: Optional SQLAlchemy session (creates new if None)

        Returns:
            Created ResearchTopic object (detached from session)
        """
        sources = sources or []
        tags = tags or []

        topic = ResearchTopic(
            topic_name=topic_name,
            summary=summary,
            sources=sources,
            tags=tags,
            research_domain_id=self.current_domain_id,
            first_researched=datetime.utcnow(),
            last_mentioned=datetime.utcnow()
        )
        
        if session:
            session.add(topic)
            session.flush()
            # Make expunge so it's detached and accessible after session closes
            session.expunge(topic)
            return topic
        else:
            with self.db.session_scope() as sess:
                sess.add(topic)
                sess.flush()
                sess.expunge(topic)
                return topic
    
    def get_topic_by_id(self, topic_id: int) -> Optional[ResearchTopic]:
        """
        Retrieve a topic by its ID.
        
        Args:
            topic_id: Topic ID
            
        Returns:
            ResearchTopic object or None if not found
        """
        with self.db.session_scope() as session:
            topic = session.query(ResearchTopic).filter(
                ResearchTopic.id == topic_id
            ).first()
            if topic:
                session.expunge(topic)
            return topic
    
    def get_topic_by_name(self, topic_name: str, exact_match: bool = True) -> Optional[ResearchTopic]:
        """
        Retrieve a topic by its name.
        
        Args:
            topic_name: Topic name to search for
            exact_match: If True, requires exact match. If False, uses case-insensitive partial match
            
        Returns:
            ResearchTopic object or None if not found
        """
        with self.db.session_scope() as session:
            if exact_match:
                topic = session.query(ResearchTopic).filter(
                    ResearchTopic.topic_name == topic_name
                ).first()
            else:
                topic = session.query(ResearchTopic).filter(
                    func.lower(ResearchTopic.topic_name).contains(topic_name.lower())
                ).first()
            if topic:
                session.expunge(topic)
            return topic
    
    def search_topics(
        self,
        query: str = None,
        tags: List[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[ResearchTopic]:
        """
        Search for topics by query string or tags.

        Args:
            query: Search query (searches in topic_name and summary)
            tags: List of tags to filter by
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of ResearchTopic objects
        """
        with self.db.session_scope() as session:
            q = session.query(ResearchTopic)

            # Filter by current domain if set
            if self.current_domain_id is not None:
                q = q.filter(ResearchTopic.research_domain_id == self.current_domain_id)

            # Apply query filter
            if query:
                q = q.filter(
                    or_(
                        func.lower(ResearchTopic.topic_name).contains(query.lower()),
                        func.lower(ResearchTopic.summary).contains(query.lower())
                    )
                )
            
            # Apply tag filter (topics that have any of the specified tags)
            # Note: SQLite JSON handling is limited, so we skip tag filtering for now
            # or check manually after fetching
            
            # Order by most recently mentioned
            q = q.order_by(ResearchTopic.last_mentioned.desc())
            
            # Apply pagination
            q = q.limit(limit).offset(offset)
            
            results = q.all()
            
            # Filter by tags manually if needed (SQLite JSON support limitation)
            if tags:
                filtered_results = []
                for topic in results:
                    if topic.tags and any(tag in topic.tags for tag in tags):
                        filtered_results.append(topic)
                results = filtered_results
            
            # Expunge all results
            for topic in results:
                session.expunge(topic)
            
            return results
    
    def get_all_topics(self, limit: int = 100, offset: int = 0) -> List[ResearchTopic]:
        """
        Get all topics, ordered by most recently mentioned.
        
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of ResearchTopic objects
        """
        with self.db.session_scope() as session:
            results = session.query(ResearchTopic).order_by(
                ResearchTopic.last_mentioned.desc()
            ).limit(limit).offset(offset).all()
            
            # Expunge all
            for topic in results:
                session.expunge(topic)
            
            return results
    
    def update_topic(
        self,
        topic_id: int,
        summary: str = None,
        sources: List[str] = None,
        tags: List[str] = None,
        update_last_mentioned: bool = True
    ) -> Optional[ResearchTopic]:
        """
        Update an existing topic.
        
        Args:
            topic_id: ID of topic to update
            summary: New summary (if provided)
            sources: New sources list (if provided)
            tags: New tags list (if provided)
            update_last_mentioned: Whether to update last_mentioned timestamp
            
        Returns:
            Updated ResearchTopic or None if not found
        """
        with self.db.session_scope() as session:
            topic = session.query(ResearchTopic).filter(
                ResearchTopic.id == topic_id
            ).first()
            
            if not topic:
                return None
            
            if summary is not None:
                topic.summary = summary
            
            if sources is not None:
                topic.sources = sources
            
            if tags is not None:
                topic.tags = tags
            
            if update_last_mentioned:
                topic.last_mentioned = datetime.utcnow()
            
            session.flush()
            session.expunge(topic)
            return topic
    
    def mark_as_mentioned(self, topic_id: int) -> Optional[ResearchTopic]:
        """
        Mark a topic as mentioned (updates last_mentioned timestamp).
        
        Args:
            topic_id: ID of topic to update
            
        Returns:
            Updated ResearchTopic or None if not found
        """
        return self.update_topic(topic_id, update_last_mentioned=True)
    
    def delete_topic(self, topic_id: int) -> bool:
        """
        Delete a topic by ID.
        
        Args:
            topic_id: ID of topic to delete
            
        Returns:
            True if deleted, False if not found
        """
        with self.db.session_scope() as session:
            topic = session.query(ResearchTopic).filter(
                ResearchTopic.id == topic_id
            ).first()
            
            if topic:
                session.delete(topic)
                return True
            return False
    
    def check_if_exists(self, topic_name: str, fuzzy: bool = False) -> bool:
        """
        Check if a topic already exists in memory.
        
        Args:
            topic_name: Topic name to check
            fuzzy: If True, uses partial matching
            
        Returns:
            True if topic exists, False otherwise
        """
        topic = self.get_topic_by_name(topic_name, exact_match=not fuzzy)
        return topic is not None
    
    def is_novel(self, topic_name: str, days_threshold: int = 7) -> bool:
        """
        Check if a topic is novel (not researched recently).
        
        Args:
            topic_name: Topic name to check
            days_threshold: Number of days to consider "recent"
            
        Returns:
            True if topic is novel or not researched within threshold
        """
        topic = self.get_topic_by_name(topic_name, exact_match=False)
        
        if not topic:
            # Topic doesn't exist, so it's novel
            return True
        
        # Check if last mentioned was more than threshold days ago
        days_since_mentioned = (datetime.utcnow() - topic.last_mentioned).days
        return days_since_mentioned > days_threshold
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.
        
        Returns:
            Dictionary with stats (total topics, recent topics, etc.)
        """
        with self.db.session_scope() as session:
            total = session.query(ResearchTopic).count()
            
            # Topics mentioned in last 7 days
            seven_days_ago = datetime.utcnow()
            from datetime import timedelta
            seven_days_ago = seven_days_ago - timedelta(days=7)
            
            recent = session.query(ResearchTopic).filter(
                ResearchTopic.last_mentioned >= seven_days_ago
            ).count()
            
            return {
                "total_topics": total,
                "recent_topics_7days": recent,
                "database_url": self.db.database_url
            }
