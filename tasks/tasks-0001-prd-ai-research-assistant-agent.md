# Task List: AI Research Assistant Agent

Based on PRD: `0001-prd-ai-research-assistant-agent.md`

## Relevant Files

- `pyproject.toml` - Project dependencies managed with uv (LangChain, LangSmith, Tavily, Telegram SDK, database drivers)
- `.env.example` - Template for environment variables (API keys, credentials)
- `config.py` - Configuration management (tool call limits, research keywords, email templates)
- `src/agent/core.py` - Main LangChain agent implementation with autonomous tool calling
- `src/agent/tools/search.py` - Web search tool implementation
- `src/agent/tools/email.py` - SMTP email tool for newsletter generation
- `src/agent/tools/memory.py` - Memory retrieval tool for checking previous research
- `src/memory/database.py` - Database connection and setup
- `src/memory/models.py` - Memory schema/models for topic tracking
- `src/memory/service.py` - Memory service layer (CRUD operations, novelty detection)
- `src/adapters/base.py` - Abstract base class for input adapters
- `src/adapters/cli.py` - CLI adapter implementation
- `src/adapters/telegram.py` - Telegram bot adapter implementation
- `src/utils/langsmith.py` - LangSmith instrumentation utilities
- `src/utils/formatters.py` - Newsletter and response formatting utilities
- `main.py` - Main entry point and orchestration
- `tests/test_agent_core.py` - Unit tests for agent core functionality
- `tests/test_memory_service.py` - Unit tests for memory service
- `tests/test_tools.py` - Unit tests for tool functions
- `tests/test_adapters.py` - Unit tests for input adapters

### Notes

- Using `uv` as the Python package manager for dependency management
- Tests should be run with `pytest` (to be added as dev dependency)
- LangSmith tracing will be enabled via environment variables
- Database choice: Start with SQLite for simplicity, can migrate to PostgreSQL or vector DB later

## Tasks

- [x] 1.0 Setup Project Infrastructure and Core Dependencies
  - [x] 1.1 Configure `pyproject.toml` with uv dependencies (langchain, langchain-openai/anthropic, langsmith, tavily-python, python-telegram-bot, etc.)
  - [x] 1.2 Create `.env.example` file with required environment variables (LANGSMITH_API_KEY, OPENAI_API_KEY, TAVILY_API_KEY, TELEGRAM_BOT_TOKEN, SMTP credentials, etc.)
  - [x] 1.3 Create `config.py` for configuration management (tool call limits, research keywords, email settings)
  - [x] 1.4 Setup project structure (create src/ directory with subdirectories: agent/, memory/, adapters/, utils/)
  - [x] 1.5 Initialize database schema file for SQLite
  - [x] 1.6 Add pytest and testing dependencies to pyproject.toml
  - [x] 1.7 Create basic README with setup instructions using uv

- [ ] 2.0 Implement Agent Core with LangChain and LangSmith Integration
  - [x] 2.1 Create `src/utils/langsmith.py` to configure LangSmith tracing and instrumentation
  - [x] 2.2 Implement `src/agent/core.py` with LangChain ReAct agent initialization
  - [x] 2.3 Add conversation memory/context management using LangChain's ConversationBufferMemory or similar
  - [x] 2.4 Implement tool call limit counter and permission request logic
  - [x] 2.5 Add error handling and graceful degradation for failed tool calls
  - [x] 2.6 Instrument agent with LangSmith callbacks to log all steps, tool calls, and LLM interactions
  - [x] 2.7 Write unit tests for agent core functionality in `tests/test_agent_core.py`

- [ ] 3.0 Build Memory System for Topic Tracking and Novelty Detection
  - [ ] 3.1 Create `src/memory/models.py` with data models for topics (ID, name, timestamps, summary, sources, tags)
  - [ ] 3.2 Implement `src/memory/database.py` for SQLite connection and initialization
  - [ ] 3.3 Create `src/memory/service.py` with CRUD operations (store topic, retrieve topic, search topics)
  - [ ] 3.4 Implement novelty detection logic (check if topic exists, compare timestamps, identify new information)
  - [ ] 3.5 Add function to mark topics as mentioned/updated with current timestamp
  - [ ] 3.6 Create memory retrieval tool in `src/agent/tools/memory.py` for agent to query previous research
  - [ ] 3.7 Write unit tests for memory service in `tests/test_memory_service.py`

- [ ] 4.0 Implement Tool Functions (Web Search and Email)
  - [ ] 4.1 Implement `src/agent/tools/search.py` as LangChain tool using Tavily API for web search
  - [ ] 4.2 Add source specification logic (GitHub, arXiv, general web) to search tool
  - [ ] 4.3 Create `src/utils/formatters.py` for newsletter template (HTML or Markdown format with sections, links, insights)
  - [ ] 4.4 Implement `src/agent/tools/email.py` for SMTP email sending with newsletter formatting
  - [ ] 4.5 Add error handling for network failures, API rate limits, and SMTP connection issues
  - [ ] 4.6 Write unit tests for tools in `tests/test_tools.py` (mock Tavily API calls and SMTP)

- [ ] 5.0 Create Modular Input Architecture (CLI and Telegram)
  - [ ] 5.1 Create `src/adapters/base.py` with abstract InputAdapter class defining interface (receive_message, send_message)
  - [ ] 5.2 Implement `src/adapters/cli.py` for terminal-based interaction (input loop, formatted output)
  - [ ] 5.3 Implement `src/adapters/telegram.py` using python-telegram-bot library (webhook or polling)
  - [ ] 5.4 Add adapter-specific response formatting (plain text for CLI, Telegram markdown for Telegram)
  - [ ] 5.5 Update `main.py` to select adapter based on command-line argument or environment variable
  - [ ] 5.6 Add session management to maintain conversation context per channel/user
  - [ ] 5.7 Write unit tests for adapters in `tests/test_adapters.py`

- [ ] 6.0 Integration and End-to-End Testing
  - [ ] 6.1 Test complete workflow: CLI command → agent research → memory storage → follow-up conversation
  - [ ] 6.2 Test Telegram workflow: send message → agent response → newsletter request → email delivery
  - [ ] 6.3 Verify LangSmith traces show all agent steps, tool calls, and decision paths
  - [ ] 6.4 Test tool call limit: verify agent pauses and requests permission after configured limit
  - [ ] 6.5 Test memory novelty: verify agent doesn't repeat information from previous sessions
  - [ ] 6.6 Test error scenarios: network failures, API errors, invalid commands
  - [ ] 6.7 Document common usage patterns and examples in README
