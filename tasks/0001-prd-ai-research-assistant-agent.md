# Product Requirements Document: AI Research Assistant Agent

## Introduction/Overview

The AI Research Assistant Agent is a conversational AI system designed to autonomously monitor and research trending topics in the AI development ecosystem. Built with LangChain and monitored via LangSmith, this agent serves as an intelligent research companion that discovers new libraries, frameworks, projects, and models, then communicates findings through natural language conversations and newsletter-style email reports.

The agent features a modular input architecture supporting multiple communication channels (CLI, Telegram, WhatsApp, web) and employs autonomous tool-calling capabilities with configurable limits to prevent token overconsumption. A key differentiator is its memory system that tracks previously researched topics to avoid redundant information delivery.

**Problem Statement:** Staying current with rapid AI development trends requires constant manual research. This agent automates the discovery and synthesis of new information while maintaining conversational context and delivering actionable insights.

## Goals

1. **Learn & Demonstrate LangChain Autonomous Tool Calling:** Implement a working example of LangChain's autonomous agent with tool-calling capabilities, fully instrumented with LangSmith for observability.

2. **Modular Input Architecture:** Create a channel-agnostic agent that can receive commands from CLI (initial), Telegram (priority), WhatsApp, and web interfaces without core logic changes.

3. **Autonomous AI Trend Research:** Enable the agent to independently search the web for trending AI topics including libraries (UI/backend), frameworks, projects, and models when instructed.

4. **Memory-Driven Novelty:** Implement a memory/database system that prevents repetitive information delivery by tracking previously researched topics.

5. **Conversational Research Interaction:** Allow natural language conversations about researched topics with the ability to request deeper dives on specific subjects.

6. **Automated Reporting:** Generate newsletter-style email reports summarizing research findings on command or via scheduled triggers (cron jobs).

## User Stories

1. **As a developer**, I want to tell the agent "research new Python AI libraries this week" via Telegram, so that I receive a curated summary without manual searching.

2. **As a user**, I want the agent to remember what it already told me about GPT-5, so that I don't receive duplicate information in subsequent research sessions.

3. **As a researcher**, I want to ask the agent follow-up questions like "tell me more about that new vector database you mentioned", so that I can explore topics conversationally.

4. **As a busy professional**, I want to command "send me a newsletter with this week's findings" and receive a formatted email report, so that I can review research on my schedule.

5. **As a cost-conscious user**, I want the agent to stop after N tool calls and ask for permission to continue, so that I avoid unexpected token consumption or infinite loops.

6. **As a developer learning LangChain**, I want to see all agent decisions, tool calls, and reasoning logged in LangSmith, so that I understand how autonomous agents operate.

7. **As a user**, I want to instruct the agent to "focus searches on GitHub trending repos" or let it autonomously decide sources, so that I can guide research direction when needed.

## Functional Requirements

### Core Agent Capabilities

1. The system must use LangChain to orchestrate a conversational agent with autonomous tool-calling capabilities.

2. The system must integrate LangSmith to log all agent steps, tool calls, LLM interactions, and decision paths.

3. The agent must implement a configurable limit on consecutive autonomous tool calls before requesting user permission to continue.

4. The agent must maintain conversation context across multiple turns within a session.

### Input Channel Architecture

5. The system must implement a modular input interface that abstracts communication channels from core agent logic.

6. The system must support CLI (terminal) input as the initial implementation.

7. The system must support Telegram as a priority messaging channel.

8. The system must be architecturally prepared to add WhatsApp and web-embedded interfaces in future iterations.

### Tool Calling - Web Search

9. The agent must integrate with a web search API (to be determined) to search the web for information.

10. The agent must autonomously decide when to use web search based on user requests (e.g., "research new AI frameworks").

11. The agent must be capable of executing multiple sequential searches to gather comprehensive information.

12. The agent must support both autonomous source selection and user-directed source specification (e.g., "search GitHub trending" or "check arXiv papers").

### Tool Calling - Email

13. The agent must integrate with an SMTP connection to send emails.

14. The agent must generate newsletter-style reports summarizing research findings when commanded.

15. The agent must format email reports with clear structure, links to sources, and key insights.

### Memory & Novelty Detection

16. The system must implement a persistent memory/database system to store researched topics and findings.

17. The agent must check memory before presenting information to avoid repeating previously delivered content.

18. The agent must indicate when information is novel versus previously researched.

19. The memory system must track timestamps, sources, and key metadata about researched topics.

### Research Focus Areas

20. The agent must be configured to research AI development trends including:
    - New AI/ML libraries (UI and backend)
    - New frameworks and tools
    - Emerging projects and repositories
    - New models and model releases
    - Significant updates to existing technologies

### Safety & Cost Controls

21. The agent must implement a configurable maximum tool call limit per user message (not per session).
    - The limit resets for each new user message/query
    - Default value: 10 tool calls per message (configurable via `MAX_TOOL_CALLS` environment variable)
    - This prevents runaway tool usage while allowing complex multi-step research within a single query
    - Example: User asks "research AI libraries" → agent can make up to 10 tool calls → limit resets on next user message

22. The system must pause and request explicit user permission when approaching the tool call limit.
    - Warning displayed at 80% of limit (e.g., "Tool call 8/10 - approaching limit")
    - Agent stops at limit and shows clear message about reaching the cap

23. The system must provide estimates of token consumption when asking for continuation permission (if implemented in future iterations).

### Scheduling & Automation

24. The system must support triggered research sessions via natural language commands.

25. The system must be compatible with cron job scheduling for periodic automated research.

## Non-Goals (Out of Scope)

1. **Initial Release Channels:** WhatsApp and web-embedded interfaces are not required for v1.0; architecture must support them, but implementation is deferred.

2. **Autonomous Decision-Making Beyond Research:** The agent will not make autonomous decisions to send emails or take actions without explicit user commands (except within configured tool call limits for research).

3. **Multi-User Support:** Initial version is single-user (yourself); multi-user architecture is not required.

4. **Real-Time Streaming:** Not required to stream results as they're found; batch summaries are acceptable.

5. **Custom ML Model Training:** The agent uses existing LLMs; no custom model training is in scope.

6. **Financial/Sensitive Data Handling:** Agent will not handle financial transactions, passwords, or sensitive personal data beyond email configuration.

7. **File System or Local Database Access:** Agent will not access local files or databases outside its designated memory store.

## Design Considerations

### Architecture Components

- **Agent Core:** LangChain agent with ReAct or OpenAI Functions-based tool calling
- **Input Adapters:** Modular interface layer (CLI, Telegram, future: WhatsApp, Web)
- **Tools:** Web search (API TBD), Email (SMTP), Memory retrieval
- **Memory Layer:** Database/vector store for topic tracking (decision needed: SQLite, PostgreSQL, ChromaDB, etc.)
- **Observability:** LangSmith integration for all agent traces

### User Interaction Flow

```
User Input (CLI/Telegram) 
  → Input Adapter 
  → Agent Core (LangChain)
  → Tool Calls (Search/Email/Memory) [with LangSmith logging]
  → Response Generation
  → Output via same channel
```

### Memory Schema (Suggested)

- **Topic ID:** Unique identifier
- **Topic Name:** e.g., "LangChain v0.3 release"
- **First Researched:** Timestamp
- **Last Mentioned:** Timestamp
- **Summary:** Key findings
- **Sources:** List of URLs
- **Tags:** Categories (library, framework, model, etc.)

## Technical Considerations

### Key Decisions Needed

1. **Memory/Database Selection:** Choose between:
   - SQLite (simple, file-based)
   - PostgreSQL (robust, scalable)
   - Vector database (ChromaDB, Pinecone) for semantic search
   - Hybrid approach (SQL + vector embeddings)

2. **LLM Provider:** OpenAI, Anthropic, or other LangChain-compatible provider

3. **Tool Call Limit:** Determine reasonable default (e.g., 10 calls) with user override capability

4. **Telegram Bot Framework:** python-telegram-bot or aiogram

### Dependencies

- **LangChain:** Core orchestration framework
- **LangSmith:** Observability and tracing
- **SMTP Library:** Built-in `smtplib` or `yagmail`
- **Search API:** To be determined (options: Tavily, SerpAPI, DuckDuckGo, Google Custom Search, Bing)
- **Database/ORM:** SQLAlchemy (if SQL) or vector DB client
- **Telegram SDK:** python-telegram-bot (priority channel)

### Configuration Management

- Environment variables for API keys (LangSmith, LLM provider, email credentials, Telegram bot token)
- Configuration file for tool call limits, research focus keywords, email templates

## Success Metrics

1. **Functional Completeness:** Agent successfully completes a full workflow: receive command → search web → store in memory → converse about findings → generate email report.

2. **LangSmith Visibility:** All agent reasoning steps, tool calls, and errors are visible in LangSmith traces with no missing instrumentation.

3. **Memory Effectiveness:** Agent correctly identifies and avoids repeating information from previous research sessions at least 90% of the time.

4. **Error Handling:** Agent gracefully handles failed tool calls (network errors, API limits) and continues or asks for guidance rather than crashing.

5. **Token Safety:** Safety mechanism successfully halts agent and requests permission before exceeding configured tool call limit in 100% of test cases.

6. **Channel Modularity:** Switching between CLI and Telegram input requires no changes to core agent logic.

7. **Learning Objective:** Developer (you) gains clear understanding of LangChain autonomous tool calling patterns through code implementation and LangSmith observation.

## Open Questions

1. **Search API Selection:** Which web search API should be used? Options to evaluate:
   - Tavily (AI-focused, clean results)
   - SerpAPI (comprehensive, paid)
   - DuckDuckGo (free, privacy-focused)
   - Google Custom Search (familiar, limited free tier)
   - Bing Search API (Microsoft ecosystem)

2. **Memory Implementation:** Should we use a SQL database, vector database, or hybrid approach for topic memory? Consider trade-offs:
   - SQL: Easier exact-match deduplication, simpler queries
   - Vector: Better semantic similarity, finds related topics
   - Hybrid: Best of both but more complex

3. **Tool Call Limit Default:** What is a reasonable default for autonomous tool call limit? (Suggested: 10-15 for initial research, 3-5 for follow-up queries)

4. **Email Frequency:** Should there be a built-in rate limit on email sending to prevent spam (e.g., max 1 newsletter per day)?

5. **Search Source Priority:** Should we define a default priority order for search sources, or let the LLM decide dynamically?

6. **Newsletter Format:** Preferred format for email reports (HTML with sections, plain text with markdown, templated design)?

7. **Cron Job Integration:** Should the cron job trigger be part of the codebase or documented as an external setup?

8. **Memory Retention Policy:** How long should topics remain in memory? Forever, or with a time-based expiration?

9. **Multi-Agent Pattern:** Would this benefit from multiple specialized agents (researcher, writer, curator) or single general-purpose agent?
