# AI Research Assistant Agent

A conversational AI agent built with LangChain that autonomously researches trending AI/ML topics, tracks findings in memory, and delivers insights via CLI, Telegram, or email newsletters.

## Features

- 🤖 **Autonomous Research**: Uses ReAct agent pattern with tool calling to search the web for AI trends
- 🧠 **Memory System**: Tracks researched topics to avoid redundant information
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
- `OPENAI_API_KEY`: Your OpenAI API key
- `TAVILY_API_KEY`: Your Tavily API key for web search
- `LANGSMITH_API_KEY`: (Optional) For LangSmith tracing
- `TELEGRAM_BOT_TOKEN`: (Optional) For Telegram integration
- SMTP credentials: (Optional) For email newsletters

### 3. Initialize Database

The SQLite database will be automatically created on first run at `./research_assistant.db`.

## Usage

### CLI Mode

```bash
uv run python main.py --mode cli
```

### Telegram Bot

```bash
uv run python main.py --mode telegram
```

## Project Structure

```
.
├── src/
│   ├── agent/
│   │   ├── core.py              # LangChain ReAct agent
│   │   └── tools/               # Agent tools (search, email, memory)
│   ├── memory/
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── database.py          # Database connection
│   │   └── service.py           # Memory operations
│   ├── adapters/
│   │   ├── base.py              # Abstract adapter interface
│   │   ├── cli.py               # CLI adapter
│   │   └── telegram.py          # Telegram adapter
│   └── utils/
│       ├── langsmith.py         # LangSmith instrumentation
│       └── formatters.py        # Newsletter formatting
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
- `MAX_TOOL_CALLS`: Maximum autonomous tool calls before requesting permission (default: 10)
- `RESEARCH_KEYWORDS`: Topics to focus research on
- `NEWSLETTER_FORMAT`: Email format (html/markdown)

## License

MIT

## Contributing

This is a personal learning project focused on understanding LangChain autonomous agents with tool calling.
