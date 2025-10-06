from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class ResearchDomain(Base):
    """SQLAlchemy model for storing research domains/topics"""

    __tablename__ = "research_domains"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    keywords = Column(JSON, default=list, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship to topics
    topics = relationship("ResearchTopic", back_populates="domain", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ResearchDomain(id={self.id}, name='{self.name}')>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "keywords": self.keywords or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_used": self.last_used.isoformat() if self.last_used else None,
        }


class ResearchTopic(Base):
    """SQLAlchemy model for storing researched topics"""

    __tablename__ = "research_topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_name = Column(String(255), nullable=False, index=True)
    research_domain_id = Column(Integer, ForeignKey("research_domains.id"), nullable=True, index=True)
    first_researched = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_mentioned = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    summary = Column(Text, nullable=True)
    sources = Column(JSON, default=list, nullable=True)
    tags = Column(JSON, default=list, nullable=True)

    # Relationship to domain
    domain = relationship("ResearchDomain", back_populates="topics")

    def __repr__(self):
        return f"<ResearchTopic(id={self.id}, topic_name='{self.topic_name}', domain_id={self.research_domain_id})>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "topic_name": self.topic_name,
            "research_domain_id": self.research_domain_id,
            "first_researched": self.first_researched.isoformat() if self.first_researched else None,
            "last_mentioned": self.last_mentioned.isoformat() if self.last_mentioned else None,
            "summary": self.summary,
            "sources": self.sources or [],
            "tags": self.tags or [],
        }
