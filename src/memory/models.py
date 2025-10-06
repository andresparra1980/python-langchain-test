from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ResearchTopic(Base):
    """SQLAlchemy model for storing researched topics"""
    
    __tablename__ = "research_topics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_name = Column(String(255), nullable=False, index=True)
    first_researched = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_mentioned = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    summary = Column(Text, nullable=True)
    sources = Column(JSON, default=list, nullable=True)
    tags = Column(JSON, default=list, nullable=True)
    
    def __repr__(self):
        return f"<ResearchTopic(id={self.id}, topic_name='{self.topic_name}', first_researched={self.first_researched})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "topic_name": self.topic_name,
            "first_researched": self.first_researched.isoformat() if self.first_researched else None,
            "last_mentioned": self.last_mentioned.isoformat() if self.last_mentioned else None,
            "summary": self.summary,
            "sources": self.sources or [],
            "tags": self.tags or [],
        }
