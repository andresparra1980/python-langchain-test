# Plan: Topic-Agnostic Research Agent

## Problem Statement
Currently, the agent is hardcoded to research AI/ML topics. We want to make it configurable to research ANY topic domain while maintaining memory isolation between different research topics.

## Goals
1. **Topic Selection at Startup**: Ask user to specify research topic if not configured
2. **Topic Switching**: Allow changing research topic mid-session
3. **Memory Isolation**: Each topic has its own memory space to avoid cross-contamination
4. **Topic Management**: Commands to view, switch, and reset topics
5. **Backward Compatibility**: Existing AI/ML focus as default option

---

## Design Overview

### 1. Topic Configuration System

#### Environment Variables (`.env`)
```bash
# Research Topic Configuration
RESEARCH_TOPIC=           # Empty = prompt on startup
RESEARCH_DOMAIN=AI/ML     # Default domain if not specified

# Example configurations:
# RESEARCH_TOPIC=cryptocurrency
# RESEARCH_TOPIC=quantum-computing
# RESEARCH_TOPIC=web3
# RESEARCH_TOPIC=biotech
```

#### Topic Metadata
```python
Topic {
    name: str           # e.g., "AI/ML", "cryptocurrency", "web3"
    description: str    # Brief description
    keywords: List[str] # Search keywords relevant to topic
    created_at: datetime
    last_used: datetime
}
```

---

### 2. Database Schema Changes

#### Option A: Topic-Scoped Memory (Recommended)
Add `topic_id` to researched topics table:

```sql
CREATE TABLE topics (
    id INTEGER PRIMARY KEY,
    topic_name TEXT NOT NULL,
    summary TEXT,
    sources TEXT,  -- JSON array
    tags TEXT,     -- JSON array
    research_domain TEXT,  -- NEW: "AI/ML", "crypto", etc.
    first_researched TIMESTAMP,
    last_mentioned TIMESTAMP
);

CREATE TABLE research_domains (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,           -- "AI/ML", "cryptocurrency", etc.
    description TEXT,
    keywords TEXT,              -- JSON array
    created_at TIMESTAMP,
    last_used TIMESTAMP
);

CREATE INDEX idx_topics_domain ON topics(research_domain);
```

#### Option B: Separate Databases Per Topic
Each topic gets its own SQLite file:
- `research_ai_ml.db`
- `research_cryptocurrency.db`
- `research_quantum_computing.db`

**Chosen Approach**: **Option A** - Single database with topic scoping
- Easier to manage
- Can search across all topics if needed
- Single backup file

---

### 3. Agent Prompt Modifications

Current (hardcoded):
```
You are an AI Research Assistant specialized in tracking trending topics in AI/ML development.
```

New (dynamic):
```python
template = f"""You are a Research Assistant specialized in tracking trending topics in {topic_domain}.

Your mission is to research new developments, projects, tools, and significant updates in the {topic_domain} ecosystem.
{topic_specific_instructions}
"""
```

#### Topic-Specific Instructions
```python
TOPIC_CONFIGS = {
    "AI/ML": {
        "description": "AI and Machine Learning development",
        "keywords": ["AI libraries", "ML frameworks", "LLM models", "vector databases"],
        "focus_areas": ["libraries", "frameworks", "models", "tools"]
    },
    "cryptocurrency": {
        "description": "Cryptocurrency and blockchain technology",
        "keywords": ["blockchain", "DeFi", "smart contracts", "crypto protocols"],
        "focus_areas": ["protocols", "DeFi projects", "new chains", "regulations"]
    },
    "web3": {
        "description": "Web3 and decentralized technologies",
        "keywords": ["decentralized apps", "NFTs", "DAOs", "IPFS"],
        "focus_areas": ["dApps", "infrastructure", "tools", "communities"]
    },
    # User can add custom topics
}
```

---

### 4. Topic Management Commands

#### CLI Commands
```
/topic                    # Show current topic
/topic list              # List all available topics with memory stats
/topic set <name>        # Switch to a different topic
/topic create <name>     # Create new topic configuration
/topic reset             # Clear memory for current topic
/topic delete <name>     # Delete a topic and its memory
```

#### Telegram Commands
```
/topic                   # Show current topic
/newtopic <name>         # Switch to new topic
/resettopic              # Clear current topic memory
```

---

### 5. Startup Flow

```
┌─────────────────────────────────────────────────┐
│ Agent Startup                                   │
└─────────────────────────────────────────────────┘
                    ↓
         ┌──────────────────┐
         │ Check RESEARCH_  │
         │ TOPIC in config  │
         └──────────────────┘
                    ↓
        ┌────────────────────┐
     No │ Topic set in .env? │ Yes
        └────────────────────┘
         ↓                   ↓
    ┌─────────┐         ┌────────────┐
    │ Prompt  │         │ Load topic │
    │ user to │         │ from config│
    │ choose  │         └────────────┘
    └─────────┘              ↓
         ↓              ┌────────────┐
    ┌─────────┐        │ Initialize │
    │ Select: │        │ with topic │
    │ 1. AI/ML│        └────────────┘
    │ 2. Crypto│            ↓
    │ 3. Custom│       ┌────────────┐
    └─────────┘        │ Agent      │
         ↓             │ ready      │
    ┌─────────┐        └────────────┘
    │ Save to │
    │ session │
    └─────────┘
         ↓
    ┌─────────┐
    │ Agent   │
    │ ready   │
    └─────────┘
```

---

### 6. Implementation Plan

#### Phase 1: Database & Configuration (2-3 hours)
- [ ] Add `research_domain` column to `topics` table
- [ ] Create `research_domains` table
- [ ] Add migration script for existing data (mark as "AI/ML")
- [ ] Create `TopicConfig` class in `config.py`
- [ ] Add topic presets to configuration

#### Phase 2: Topic Selection System (2 hours)
- [ ] Create `TopicManager` service class
- [ ] Implement topic switching logic
- [ ] Add topic validation
- [ ] Create topic creation/deletion methods

#### Phase 3: Agent Integration (2 hours)
- [ ] Make agent prompt template dynamic
- [ ] Update memory service to filter by topic
- [ ] Add topic context to agent initialization
- [ ] Update tool descriptions to be topic-aware

#### Phase 4: CLI/UI Integration (2 hours)
- [ ] Add topic selection on startup (if not configured)
- [ ] Implement `/topic` commands in CLI
- [ ] Add topic display in CLI prompt
- [ ] Update Telegram adapter with topic commands

#### Phase 5: Testing & Documentation (1-2 hours)
- [ ] Write tests for topic management
- [ ] Update README with topic configuration
- [ ] Add example configurations
- [ ] Test topic switching scenarios

**Total Estimated Time**: 9-11 hours

---

### 7. User Experience Examples

#### Example 1: First-time user (no topic configured)
```
$ uv run python main.py

╔════════════════════════════════════════════════╗
║     Research Assistant - Topic Selection      ║
╚════════════════════════════════════════════════╝

What would you like to research?

  1. AI/ML Development (default)
  2. Cryptocurrency & Blockchain
  3. Web3 & Decentralized Tech
  4. Custom topic (you specify)

Your choice (1-4): 1

✓ Configured for AI/ML Development
✓ Agent initialized with 0 topics in memory

You: research langchain features
...
```

#### Example 2: Switching topics mid-session
```
You: /topic
Current topic: AI/ML Development
Topics researched: 15
Last research: 2 minutes ago

You: /topic set cryptocurrency
⚠️  Switching topics will change your research context.
   Continue? (y/n): y

✓ Switched to: Cryptocurrency & Blockchain
✓ Memory loaded: 3 topics

You: research new defi protocols
...
```

#### Example 3: Creating custom topic
```
You: /topic create quantum-computing

Creating new research topic...

Topic name: quantum-computing
Description: Quantum computing and quantum algorithms
Keywords (comma-separated): quantum, qubits, quantum algorithms, quantum hardware

✓ Topic created: quantum-computing
✓ Switched to new topic

You: research IBM quantum systems
...
```

---

### 8. Configuration File Structure

#### `config/topics.json` (new file)
```json
{
  "topics": {
    "ai-ml": {
      "name": "AI/ML Development",
      "description": "Artificial Intelligence and Machine Learning",
      "keywords": [
        "AI libraries",
        "ML frameworks",
        "LLM models",
        "vector databases",
        "transformers"
      ],
      "focus_areas": [
        "New libraries and frameworks",
        "Model releases",
        "Research papers",
        "Developer tools"
      ]
    },
    "cryptocurrency": {
      "name": "Cryptocurrency & Blockchain",
      "description": "Crypto assets and blockchain technology",
      "keywords": [
        "blockchain",
        "DeFi",
        "smart contracts",
        "crypto protocols",
        "NFTs"
      ],
      "focus_areas": [
        "New protocols",
        "DeFi projects",
        "Regulations",
        "Exchange updates"
      ]
    }
  },
  "active_topic": "ai-ml"
}
```

---

### 9. Breaking Changes & Migration

#### For Existing Users
1. First run will prompt: "Existing data found. Mark as 'AI/ML' topic? (y/n)"
2. If yes: Add `research_domain='AI/ML'` to all existing topics
3. Create migration script: `migrate_to_topic_system.py`

#### Migration Script
```python
# scripts/migrate_to_topic_system.py
from src.memory.database import Database
from src.memory.service import MemoryService

def migrate():
    """Migrate existing data to topic-scoped system"""
    db = Database()
    # Add research_domain column
    # Set all existing topics to 'AI/ML'
    # Create default topic config
```

---

### 10. Benefits

✅ **Versatility**: Research any topic, not just AI/ML
✅ **Organization**: Separate memory per topic domain
✅ **Flexibility**: Easy to switch between research interests
✅ **Scalability**: Add new topics without code changes
✅ **User Control**: Explicit topic management
✅ **Memory Efficiency**: Only load relevant topic data

---

### 11. Potential Challenges

⚠️ **Challenge 1**: Tool descriptions are somewhat AI-specific
**Solution**: Make tool descriptions more generic or topic-aware

⚠️ **Challenge 2**: Existing users have AI/ML data
**Solution**: Automatic migration on first run

⚠️ **Challenge 3**: Newsletter keywords are AI-focused
**Solution**: Make keywords configurable per topic

⚠️ **Challenge 4**: Topic switching mid-conversation might confuse LLM
**Solution**: Clear conversation memory when switching topics

---

### 12. Future Enhancements

🚀 **Phase 2 Features** (after initial release):
- Cross-topic search: "Find anything about Python"
- Topic templates: Pre-configured topic packs
- Topic sharing: Export/import topic configurations
- Multi-topic mode: Research multiple topics simultaneously
- Topic analytics: Stats and trends per topic
- Smart suggestions: Recommend related topics

---

## Next Steps

1. **Review this plan** - Get feedback on approach
2. **Approve database changes** - Confirm schema modifications
3. **Start Phase 1** - Begin with database updates
4. **Iterative development** - Implement phase by phase
5. **Test each phase** - Ensure backward compatibility

---

## Questions to Address

1. Should we support multiple topics in a single session?
2. Should topic switching clear conversation memory?
3. Should we allow topic merging/splitting?
4. Should newsletters be per-topic or cross-topic?
5. Should we add topic-specific search sources?
