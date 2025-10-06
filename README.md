# AI Research Assistant Agent

A conversational AI agent built with LangChain that autonomously researches trending topics in any domain, tracks findings in memory, and delivers insights via CLI, Telegram, or email newsletters.

## Features

- 🤖 **Autonomous Research**: Uses ReAct agent pattern with tool calling to search the web for trends
- 🎯 **Topic-Agnostic**: Research any domain - AI/ML, crypto, web3, quantum computing, or custom topics
- 🧠 **Memory System**: Tracks researched topics per domain to avoid redundant information
- 📊 **LangSmith Observability**: Full tracing of agent decisions and tool calls
- 💬 **Multi-Channel Input**: CLI and Telegram support with modular architecture
- 📧 **Newsletter Generation**: Automated email reports of research findings
- 🔍 **Web Search**: Integrated with Tavily for high-quality search results

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

## Setup

### 1. Install Dependencies

```bash
# Install dependencies using uv
uv sync

# Or install with dev dependencies
uv sync --extra dev
```

### 2. Configure Environment Variables

Copy the example environment file and fill in your API keys:

```bash
cp .env.example .env
```

Required environment variables:
- `LLM_PROVIDER`: Choose "openai" or "openrouter" (default: openai)
- `OPENAI_API_KEY`: Your OpenAI API key (if using OpenAI)
- `OPENROUTER_API_KEY`: Your OpenRouter API key (if using OpenRouter)
- `TAVILY_API_KEY`: Your Tavily API key for web search
- `LLM_MODEL`: Model to use (e.g., gpt-4o-mini, anthropic/claude-3-5-sonnet)

Optional environment variables:
- `LANGSMITH_API_KEY`: For LangSmith tracing
- `TELEGRAM_BOT_TOKEN`: For Telegram integration
- SMTP credentials: For email newsletters

### 3. Choose Your LLM Provider

#### Option A: OpenAI (Default)
```bash
# In your .env file:
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
```

#### Option B: OpenRouter (Access Multiple Models)
```bash
# In your .env file:
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-...
LLM_MODEL=anthropic/claude-3-5-sonnet
# Or use: openai/gpt-4o, meta-llama/llama-3.1-70b-instruct, etc.
```

Get your OpenRouter API key at: https://openrouter.ai/keys
Browse available models at: https://openrouter.ai/models

### 4. Select Research Topic

The agent can research any topic domain. Choose at startup or configure in `.env`:

```bash
# Leave empty to be prompted at startup (recommended for first run)
RESEARCH_TOPIC=

# Or specify a preset topic:
RESEARCH_TOPIC=ai-ml              # AI/ML development (default)
RESEARCH_TOPIC=cryptocurrency     # Crypto & blockchain
RESEARCH_TOPIC=web3               # Web3 & decentralized tech
RESEARCH_TOPIC=quantum-computing  # Quantum computing

# Or use a custom topic:
RESEARCH_TOPIC=biotech            # Any domain you choose
```

**Available Preset Topics:**
- **ai-ml**: AI and Machine Learning (libraries, frameworks, models, tools)
- **cryptocurrency**: Blockchain, DeFi, smart contracts, crypto protocols
- **web3**: Decentralized apps, IPFS, Web3 infrastructure
- **quantum-computing**: Quantum hardware, algorithms, research

**Custom Topics**: You can research any domain! When prompted at startup, select option 5 to create your own research topic with custom keywords and focus areas.

### 5. Initialize Database

Run the migration script to set up the database with topic support:

```bash
uv run python scripts/migrate_to_topic_system.py
```

This will:
- Create the `research_domains` and `research_topics` tables
- Migrate any existing data to the default AI/ML domain
- Set up preset topic domains (AI/ML, crypto, web3, quantum computing)

The SQLite database is stored at `./research_assistant.db`.

## Usage

### CLI Mode (Default)

Start the interactive CLI interface:

```bash
uv run python main.py
```

Or with reduced verbosity:

```bash
uv run python main.py --quiet
```

### Telegram Bot

Start the Telegram bot:

```bash
uv run python main.py --telegram
```

Or with a custom bot token:

```bash
uv run python main.py --telegram --token YOUR_BOT_TOKEN
```

### Getting Help

```bash
uv run python main.py --help
```

### Example Commands in CLI

Once the CLI starts, you can:
- Ask research questions: `"Research new Python AI libraries"`
- Search specific sources: `"Search GitHub for vector databases"`
- Check memory: `"What did we discuss about LangChain?"`
- Request newsletters: `"Send me a newsletter with recent findings"`
- **Topic management**:
  - `/topic` - Show current research topic
  - `/topic list` - List all available topics
  - `/topic set <name>` - Switch to a different topic (requires restart)
- Get help: Type `help`
- Clear session: Type `clear`
- Exit: Type `exit` or `quit`

## Topic Management

The agent features a powerful topic management system that allows you to research any domain:

### How It Works
1. **Topic Selection**: Choose your research domain at startup or configure in `.env`
2. **Memory Isolation**: Each topic has its own memory space - research on crypto won't mix with AI/ML findings
3. **Dynamic Prompts**: Agent instructions automatically adapt to your selected topic
4. **Preset Topics**: Use built-in presets or create custom research domains

### Switching Topics
To research a different domain:
1. Update `RESEARCH_TOPIC` in your `.env` file
2. Restart the agent
3. Or leave it empty and select interactively at startup

### Topic Commands
- `/topic` - View current topic and stats
- `/topic list` - See all available topics with memory counts
- `/topic set <name>` - Note this requires restarting the agent

## Project Structure

```
.
├── src/
│   ├── agent/
│   │   ├── core.py              # LangChain ReAct agent
│   │   └── tools/               # Agent tools (search, email, memory)
│   ├── memory/
│   │   ├── models.py            # SQLAlchemy models (topics, domains)
│   │   ├── database.py          # Database connection
│   │   └── service.py           # Memory operations
│   ├── topic/
│   │   ├── manager.py           # Topic management system
│   │   └── selector.py          # Interactive topic selection
│   ├── adapters/
│   │   ├── base.py              # Abstract adapter interface
│   │   ├── cli.py               # CLI adapter
│   │   └── telegram.py          # Telegram adapter
│   └── utils/
│       ├── langsmith.py         # LangSmith instrumentation
│       └── formatters.py        # Newsletter formatting
├── scripts/
│   └── migrate_to_topic_system.py  # Database migration
├── tests/                       # Unit tests
├── config.py                    # Configuration management
├── main.py                      # Entry point
└── pyproject.toml              # Dependencies
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/test_agent_core.py
```

## Development

### Adding Dependencies

```bash
# Add a new dependency
uv add package-name

# Add a dev dependency
uv add --dev package-name
```

### Code Quality

```bash
# Run tests before committing
uv run pytest
```

## Configuration

Key settings in `config.py`:
- `MAX_TOOL_CALLS`: Maximum autonomous tool calls **per user message** (default: 10)
  - The limit resets for each new message you send to the agent
  - This prevents runaway tool usage while allowing complex research within a single query
  - Example: You ask "research AI libraries" → agent can use up to 10 tools → when you ask the next question, the counter resets
- `RESEARCH_KEYWORDS`: Topics to focus research on
- `NEWSLETTER_FORMAT`: Email format (html/markdown/text)
- `LLM_PROVIDER`: Choose between "openai" or "openrouter"
- `LLM_MODEL`: Which model to use (e.g., gpt-4o-mini, anthropic/claude-3-5-sonnet)

## License

MIT

## Contributing

This is a personal learning project focused on understanding LangChain autonomous agents with tool calling.
