import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class for AI Research Assistant Agent"""
    
    # LangSmith Configuration
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
    LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "ai-research-assistant")
    LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "true").lower() == "true"
    
    # LLM Provider
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
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
    
    # Research Keywords/Focus Areas
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
        required_vars = [
            ("OPENAI_API_KEY", cls.OPENAI_API_KEY),
            ("TAVILY_API_KEY", cls.TAVILY_API_KEY),
        ]
        
        missing = [var_name for var_name, var_value in required_vars if not var_value]
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                "Please check your .env file or environment settings."
            )
        
        return True


config = Config()
