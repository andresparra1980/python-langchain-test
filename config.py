import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class for AI Research Assistant Agent"""
    
    # LangSmith Configuration
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
    LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "ai-research-assistant")
    LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "true").lower() == "true"
    
    # LLM Provider Configuration
    # Supports both OpenAI and OpenRouter
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()  # "openai" or "openrouter"

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # OpenRouter Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

    # Model Configuration (works for both providers)
    # For OpenAI: gpt-4o-mini, gpt-4o, gpt-4-turbo, etc.
    # For OpenRouter: openai/gpt-4o-mini, anthropic/claude-3-5-sonnet, etc.
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    
    # Search API
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # SMTP Email Configuration
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL")
    SMTP_TO_EMAIL = os.getenv("SMTP_TO_EMAIL")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./research_assistant.db")
    
    # Agent Configuration
    MAX_TOOL_CALLS = int(os.getenv("MAX_TOOL_CALLS", "10"))
    RESEARCH_MODE = os.getenv("RESEARCH_MODE", "autonomous")

    # Research Topic Configuration
    RESEARCH_TOPIC = os.getenv("RESEARCH_TOPIC", "").strip()  # Empty = prompt on startup
    # Preset options: ai-ml, cryptocurrency, web3, quantum-computing, or custom

    # Research Keywords/Focus Areas (deprecated - now managed by TopicManager)
    RESEARCH_KEYWORDS = [
        "AI libraries",
        "ML frameworks",
        "LLM models",
        "vector databases",
        "AI tools",
        "machine learning",
        "deep learning",
        "transformers",
        "diffusion models",
        "AI agents",
    ]
    
    # Newsletter Template Settings
    NEWSLETTER_SUBJECT = "AI Research Digest - {date}"
    NEWSLETTER_FORMAT = os.getenv("NEWSLETTER_FORMAT", "html")
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        # Check LLM provider-specific requirements
        if cls.LLM_PROVIDER == "openrouter":
            if not cls.OPENROUTER_API_KEY:
                raise ValueError(
                    "OPENROUTER_API_KEY is required when LLM_PROVIDER=openrouter.\n"
                    "Please set OPENROUTER_API_KEY in your .env file."
                )
        else:  # Default to OpenAI
            if not cls.OPENAI_API_KEY:
                raise ValueError(
                    "OPENAI_API_KEY is required when LLM_PROVIDER=openai (or not set).\n"
                    "Please set OPENAI_API_KEY in your .env file."
                )

        # Check other required vars
        if not cls.TAVILY_API_KEY:
            raise ValueError(
                "TAVILY_API_KEY is required for web search functionality.\n"
                "Please set TAVILY_API_KEY in your .env file."
            )

        return True


config = Config()
