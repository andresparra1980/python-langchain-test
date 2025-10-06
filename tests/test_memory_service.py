import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.memory.models import Base, ResearchTopic
from src.memory.database import Database
from src.memory.service import MemoryService


@pytest.fixture
def in_memory_db():
    """Create an in-memory database for testing"""
    db = Database(database_url="sqlite:///:memory:")
    yield db
    db.close()


@pytest.fixture
def memory_service(in_memory_db):
    """Create a MemoryService instance with in-memory database"""
    service = MemoryService()
    service.db = in_memory_db
    return service


@pytest.fixture
def sample_topic_data():
    """Sample topic data for testing"""
    return {
        "topic_name": "LangChain v0.3",
        "summary": "New version of LangChain with improved features",
        "sources": ["https://langchain.com", "https://github.com/langchain"],
        "tags": ["langchain", "framework", "llm"]
    }


class TestDatabase:
    """Test Database class"""
    
    def test_init_creates_tables(self, in_memory_db):
        """Test database initialization creates tables"""
        # Check that tables exist
        assert "research_topics" in Base.metadata.tables
    
    def test_session_scope_commits_on_success(self, in_memory_db):
        """Test session scope commits changes"""
        with in_memory_db.session_scope() as session:
            topic = ResearchTopic(
                topic_name="Test Topic",
                summary="Test summary"
            )
            session.add(topic)
        
        # Verify topic was committed
        with in_memory_db.session_scope() as session:
            result = session.query(ResearchTopic).filter(
                ResearchTopic.topic_name == "Test Topic"
            ).first()
            assert result is not None
            assert result.summary == "Test summary"
    
    def test_session_scope_rolls_back_on_error(self, in_memory_db):
        """Test session scope rolls back on exception"""
        try:
            with in_memory_db.session_scope() as session:
                topic = ResearchTopic(
                    topic_name="Test Topic",
                    summary="Test"
                )
                session.add(topic)
                raise Exception("Test exception")
        except Exception:
            pass
        
        # Verify topic was not committed
        with in_memory_db.session_scope() as session:
            count = session.query(ResearchTopic).count()
            assert count == 0


class TestMemoryService:
    """Test MemoryService class"""
    
    def test_store_topic(self, memory_service, sample_topic_data):
        """Test storing a new topic"""
        topic = memory_service.store_topic(**sample_topic_data)
        
        assert topic.id is not None
        assert topic.topic_name == sample_topic_data["topic_name"]
        assert topic.summary == sample_topic_data["summary"]
        assert topic.sources == sample_topic_data["sources"]
        assert topic.tags == sample_topic_data["tags"]
        assert topic.first_researched is not None
        assert topic.last_mentioned is not None
    
    def test_store_topic_with_defaults(self, memory_service):
        """Test storing topic with minimal data"""
        topic = memory_service.store_topic(topic_name="Minimal Topic")
        
        assert topic.id is not None
        assert topic.topic_name == "Minimal Topic"
        assert topic.summary is None
        assert topic.sources == []
        assert topic.tags == []
    
    def test_get_topic_by_id(self, memory_service, sample_topic_data):
        """Test retrieving topic by ID"""
        created = memory_service.store_topic(**sample_topic_data)
        
        retrieved = memory_service.get_topic_by_id(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.topic_name == sample_topic_data["topic_name"]
    
    def test_get_topic_by_id_not_found(self, memory_service):
        """Test retrieving non-existent topic returns None"""
        result = memory_service.get_topic_by_id(999)
        assert result is None
    
    def test_get_topic_by_name_exact(self, memory_service, sample_topic_data):
        """Test retrieving topic by exact name"""
        memory_service.store_topic(**sample_topic_data)
        
        retrieved = memory_service.get_topic_by_name("LangChain v0.3", exact_match=True)
        
        assert retrieved is not None
        assert retrieved.topic_name == "LangChain v0.3"
    
    def test_get_topic_by_name_fuzzy(self, memory_service, sample_topic_data):
        """Test retrieving topic by partial name"""
        memory_service.store_topic(**sample_topic_data)
        
        retrieved = memory_service.get_topic_by_name("langchain", exact_match=False)
        
        assert retrieved is not None
        assert "LangChain" in retrieved.topic_name
    
    def test_get_topic_by_name_not_found(self, memory_service):
        """Test retrieving non-existent topic by name"""
        result = memory_service.get_topic_by_name("Nonexistent")
        assert result is None
    
    def test_search_topics_by_query(self, memory_service):
        """Test searching topics by query"""
        memory_service.store_topic(
            topic_name="LangChain Framework",
            summary="Python framework for LLMs"
        )
        memory_service.store_topic(
            topic_name="Vector Database",
            summary="Database for embeddings"
        )
        
        results = memory_service.search_topics(query="langchain")
        
        assert len(results) == 1
        assert "LangChain" in results[0].topic_name
    
    def test_search_topics_by_tags(self, memory_service):
        """Test searching topics by tags"""
        memory_service.store_topic(
            topic_name="Topic 1",
            tags=["python", "framework"]
        )
        memory_service.store_topic(
            topic_name="Topic 2",
            tags=["javascript", "library"]
        )
        
        results = memory_service.search_topics(tags=["python"])
        
        assert len(results) == 1
        assert results[0].topic_name == "Topic 1"
    
    def test_search_topics_with_limit(self, memory_service):
        """Test search with limit parameter"""
        for i in range(5):
            memory_service.store_topic(topic_name=f"Topic {i}")
        
        results = memory_service.search_topics(limit=3)
        
        assert len(results) == 3
    
    def test_search_topics_empty_result(self, memory_service):
        """Test search with no matching results"""
        results = memory_service.search_topics(query="nonexistent")
        assert len(results) == 0
    
    def test_get_all_topics(self, memory_service):
        """Test retrieving all topics"""
        for i in range(3):
            memory_service.store_topic(topic_name=f"Topic {i}")
        
        results = memory_service.get_all_topics()
        
        assert len(results) == 3
    
    def test_get_all_topics_ordered_by_recent(self, memory_service):
        """Test topics are ordered by most recently mentioned"""
        topic1 = memory_service.store_topic(topic_name="Old Topic")
        topic2 = memory_service.store_topic(topic_name="New Topic")
        
        # Update topic1 to be more recent
        memory_service.mark_as_mentioned(topic1.id)
        
        results = memory_service.get_all_topics()
        
        # Most recently mentioned should be first
        assert results[0].topic_name == "Old Topic"
    
    def test_update_topic(self, memory_service, sample_topic_data):
        """Test updating a topic"""
        topic = memory_service.store_topic(**sample_topic_data)
        
        updated = memory_service.update_topic(
            topic.id,
            summary="Updated summary",
            tags=["new", "tags"]
        )
        
        assert updated is not None
        assert updated.summary == "Updated summary"
        assert updated.tags == ["new", "tags"]
    
    def test_update_topic_not_found(self, memory_service):
        """Test updating non-existent topic"""
        result = memory_service.update_topic(999, summary="Test")
        assert result is None
    
    def test_update_topic_updates_last_mentioned(self, memory_service):
        """Test that update changes last_mentioned timestamp"""
        topic = memory_service.store_topic(topic_name="Test")
        original_time = topic.last_mentioned
        
        # Wait a tiny bit to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        updated = memory_service.update_topic(
            topic.id,
            summary="New summary",
            update_last_mentioned=True
        )
        
        assert updated.last_mentioned > original_time
    
    def test_mark_as_mentioned(self, memory_service):
        """Test marking topic as mentioned"""
        topic = memory_service.store_topic(topic_name="Test Topic")
        original_time = topic.last_mentioned
        
        import time
        time.sleep(0.01)
        
        updated = memory_service.mark_as_mentioned(topic.id)
        
        assert updated is not None
        assert updated.last_mentioned > original_time
    
    def test_delete_topic(self, memory_service, sample_topic_data):
        """Test deleting a topic"""
        topic = memory_service.store_topic(**sample_topic_data)
        
        result = memory_service.delete_topic(topic.id)
        
        assert result is True
        
        # Verify topic is deleted
        retrieved = memory_service.get_topic_by_id(topic.id)
        assert retrieved is None
    
    def test_delete_topic_not_found(self, memory_service):
        """Test deleting non-existent topic"""
        result = memory_service.delete_topic(999)
        assert result is False
    
    def test_check_if_exists_true(self, memory_service):
        """Test checking if topic exists"""
        memory_service.store_topic(topic_name="Existing Topic")
        
        exists = memory_service.check_if_exists("Existing Topic")
        
        assert exists is True
    
    def test_check_if_exists_false(self, memory_service):
        """Test checking non-existent topic"""
        exists = memory_service.check_if_exists("Nonexistent")
        assert exists is False
    
    def test_check_if_exists_fuzzy(self, memory_service):
        """Test fuzzy existence check"""
        memory_service.store_topic(topic_name="LangChain Framework")
        
        exists = memory_service.check_if_exists("langchain", fuzzy=True)
        
        assert exists is True
    
    def test_is_novel_new_topic(self, memory_service):
        """Test novelty check for new topic"""
        is_novel = memory_service.is_novel("Brand New Topic")
        assert is_novel is True
    
    def test_is_novel_recent_topic(self, memory_service):
        """Test novelty check for recently mentioned topic"""
        memory_service.store_topic(topic_name="Recent Topic")
        
        is_novel = memory_service.is_novel("Recent Topic", days_threshold=7)
        
        assert is_novel is False
    
    def test_is_novel_old_topic(self, memory_service):
        """Test novelty check for old topic"""
        # Create topic with old timestamp
        with memory_service.db.session_scope() as session:
            old_time = datetime.utcnow() - timedelta(days=10)
            topic = ResearchTopic(
                topic_name="Old Topic",
                first_researched=old_time,
                last_mentioned=old_time
            )
            session.add(topic)
        
        is_novel = memory_service.is_novel("Old Topic", days_threshold=7)
        
        assert is_novel is True
    
    def test_get_stats(self, memory_service):
        """Test getting memory statistics"""
        # Create some topics
        memory_service.store_topic(topic_name="Topic 1")
        memory_service.store_topic(topic_name="Topic 2")
        
        # Create an old topic
        with memory_service.db.session_scope() as session:
            old_time = datetime.utcnow() - timedelta(days=10)
            topic = ResearchTopic(
                topic_name="Old Topic",
                first_researched=old_time,
                last_mentioned=old_time
            )
            session.add(topic)
        
        stats = memory_service.get_stats()
        
        assert stats["total_topics"] == 3
        assert stats["recent_topics_7days"] == 2
        assert "database_url" in stats


class TestResearchTopicModel:
    """Test ResearchTopic model"""
    
    def test_to_dict(self, memory_service):
        """Test converting topic to dictionary"""
        topic = memory_service.store_topic(
            topic_name="Test Topic",
            summary="Test summary",
            sources=["url1", "url2"],
            tags=["tag1", "tag2"]
        )
        
        topic_dict = topic.to_dict()
        
        assert topic_dict["id"] == topic.id
        assert topic_dict["topic_name"] == "Test Topic"
        assert topic_dict["summary"] == "Test summary"
        assert topic_dict["sources"] == ["url1", "url2"]
        assert topic_dict["tags"] == ["tag1", "tag2"]
        assert "first_researched" in topic_dict
        assert "last_mentioned" in topic_dict
    
    def test_repr(self, memory_service):
        """Test string representation"""
        topic = memory_service.store_topic(topic_name="Test")
        
        repr_str = repr(topic)
        
        assert "ResearchTopic" in repr_str
        assert "Test" in repr_str
