-- SQLite schema for AI Research Assistant
-- This file documents the database structure

CREATE TABLE IF NOT EXISTS research_topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_name VARCHAR(255) NOT NULL,
    first_researched DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_mentioned DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    summary TEXT,
    sources JSON,
    tags JSON
);

CREATE INDEX IF NOT EXISTS idx_topic_name ON research_topics(topic_name);
CREATE INDEX IF NOT EXISTS idx_first_researched ON research_topics(first_researched);
CREATE INDEX IF NOT EXISTS idx_last_mentioned ON research_topics(last_mentioned);
