"""Unit tests for agent tools (search, email, memory)"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime

from src.agent.tools.search import SearchTools, create_search_tools
from src.agent.tools.email import EmailTools, create_email_tools
from src.agent.tools.memory import MemoryTools, create_memory_tools


class TestSearchTools:
    """Tests for SearchTools class"""

    @pytest.fixture
    def mock_tavily_client(self):
        """Mock Tavily client"""
        with patch("src.agent.tools.search.TavilyClient") as mock:
            yield mock

    @pytest.fixture
    def search_tools(self, mock_tavily_client):
        """Create SearchTools instance with mocked Tavily client"""
        with patch("src.agent.tools.search.config") as mock_config:
            mock_config.TAVILY_API_KEY = "test_key"
            tools = SearchTools()
            return tools

    def test_search_tools_initialization(self, mock_tavily_client):
        """Test SearchTools initializes with API key"""
        with patch("src.agent.tools.search.config") as mock_config:
            mock_config.TAVILY_API_KEY = "test_key"
            tools = SearchTools()
            assert tools.client is not None

    def test_search_tools_missing_api_key(self, mock_tavily_client):
        """Test SearchTools raises error when API key is missing"""
        with patch("src.agent.tools.search.config") as mock_config:
            mock_config.TAVILY_API_KEY = None
            with pytest.raises(ValueError, match="TAVILY_API_KEY not found"):
                SearchTools()

    def test_search_web_success(self, search_tools):
        """Test successful web search"""
        # Mock response
        search_tools.client.search.return_value = {
            "results": [
                {
                    "title": "Test Result 1",
                    "url": "https://example.com/1",
                    "content": "This is test content for result 1"
                },
                {
                    "title": "Test Result 2",
                    "url": "https://example.com/2",
                    "content": "This is test content for result 2"
                }
            ]
        }

        result = search_tools.search_web("test query")

        assert "Search results for 'test query'" in result
        assert "Test Result 1" in result
        assert "https://example.com/1" in result
        assert "This is test content for result 1" in result

    def test_search_web_no_results(self, search_tools):
        """Test web search with no results"""
        search_tools.client.search.return_value = {"results": []}

        result = search_tools.search_web("test query")

        assert "No results found for query: test query" in result

    def test_search_web_error(self, search_tools):
        """Test web search handles errors gracefully"""
        search_tools.client.search.side_effect = Exception("API Error")

        result = search_tools.search_web("test query")

        assert "Error performing search" in result
        assert "API Error" in result

    def test_search_web_long_content_truncation(self, search_tools):
        """Test that long content is truncated"""
        long_content = "A" * 500  # Content longer than 300 chars

        search_tools.client.search.return_value = {
            "results": [
                {
                    "title": "Test",
                    "url": "https://example.com",
                    "content": long_content
                }
            ]
        }

        result = search_tools.search_web("test")

        assert "..." in result  # Should have ellipsis from truncation
        assert len(result) < len(long_content)  # Should be shorter

    def test_search_github(self, search_tools):
        """Test GitHub search"""
        search_tools.client.search.return_value = {
            "results": [
                {
                    "title": "langchain/langchain",
                    "url": "https://github.com/langchain/langchain",
                    "content": "Build applications with LLMs"
                }
            ]
        }

        result = search_tools.search_github("langchain")

        assert "GitHub search results for 'langchain'" in result
        assert "langchain/langchain" in result
        assert "github.com" in result

    def test_search_arxiv(self, search_tools):
        """Test arXiv search"""
        search_tools.client.search.return_value = {
            "results": [
                {
                    "title": "Attention Is All You Need",
                    "url": "https://arxiv.org/abs/1706.03762",
                    "content": "The dominant sequence transduction models..."
                }
            ]
        }

        result = search_tools.search_arxiv("transformers")

        assert "arXiv search results for 'transformers'" in result
        assert "Attention Is All You Need" in result
        assert "arxiv.org" in result

    def test_search_news(self, search_tools):
        """Test news search"""
        search_tools.client.search.return_value = {
            "results": [
                {
                    "title": "Latest AI Developments",
                    "url": "https://news.example.com/ai",
                    "content": "Recent breakthroughs in AI..."
                }
            ]
        }

        result = search_tools.search_news("AI developments")

        assert "Recent news for 'AI developments'" in result
        assert "Latest AI Developments" in result

    def test_get_tools_returns_list(self, search_tools):
        """Test get_tools returns a list of Tool objects"""
        tools = search_tools.get_tools()

        assert isinstance(tools, list)
        assert len(tools) == 4  # web, github, arxiv, news
        assert all(hasattr(tool, "name") for tool in tools)
        assert all(hasattr(tool, "func") for tool in tools)

    def test_create_search_tools_convenience_function(self, mock_tavily_client):
        """Test create_search_tools convenience function"""
        with patch("src.agent.tools.search.config") as mock_config:
            mock_config.TAVILY_API_KEY = "test_key"
            tools = create_search_tools()

            assert isinstance(tools, list)
            assert len(tools) == 4


class TestEmailTools:
    """Tests for EmailTools class"""

    @pytest.fixture
    def email_tools(self):
        """Create EmailTools instance with mocked config"""
        with patch("src.agent.tools.email.config") as mock_config:
            mock_config.SMTP_HOST = "smtp.example.com"
            mock_config.SMTP_PORT = 587
            mock_config.SMTP_USERNAME = "test@example.com"
            mock_config.SMTP_PASSWORD = "password"
            mock_config.SMTP_FROM_EMAIL = "test@example.com"
            mock_config.SMTP_TO_EMAIL = "recipient@example.com"
            mock_config.SMTP_USE_TLS = True
            mock_config.NEWSLETTER_SUBJECT = "Test Newsletter - {date}"
            mock_config.NEWSLETTER_FORMAT = "html"
            return EmailTools()

    def test_validate_config_success(self, email_tools):
        """Test configuration validation succeeds with valid config"""
        assert email_tools._validate_config() is True

    def test_validate_config_missing_fields(self):
        """Test configuration validation fails with missing fields"""
        with patch("src.agent.tools.email.config") as mock_config:
            mock_config.SMTP_HOST = None
            mock_config.SMTP_USERNAME = None
            mock_config.SMTP_PASSWORD = None

            tools = EmailTools()

            with pytest.raises(ValueError, match="Missing required email configuration"):
                tools._validate_config()

    @patch("src.agent.tools.email.smtplib.SMTP")
    def test_send_email_success(self, mock_smtp, email_tools):
        """Test successful email sending"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = email_tools._send_email(
            subject="Test Subject",
            body="Test Body",
            content_type="plain"
        )

        assert "Email sent successfully" in result
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()

    @patch("src.agent.tools.email.smtplib.SMTP")
    def test_send_email_authentication_error(self, mock_smtp, email_tools):
        """Test email sending handles authentication errors"""
        mock_smtp.return_value.__enter__.return_value.login.side_effect = (
            Exception("Authentication failed")
        )

        result = email_tools._send_email(
            subject="Test",
            body="Test",
            content_type="plain"
        )

        assert "Error sending email" in result

    @patch("src.agent.tools.email.smtplib.SMTP")
    def test_send_email_no_recipient(self, mock_smtp):
        """Test email sending fails when no recipient is specified"""
        with patch("src.agent.tools.email.config") as mock_config:
            mock_config.SMTP_HOST = "smtp.example.com"
            mock_config.SMTP_PORT = 587
            mock_config.SMTP_USERNAME = "test@example.com"
            mock_config.SMTP_PASSWORD = "password"
            mock_config.SMTP_FROM_EMAIL = "test@example.com"
            mock_config.SMTP_TO_EMAIL = None  # No recipient
            mock_config.SMTP_USE_TLS = True

            tools = EmailTools()

            result = tools._send_email(
                subject="Test",
                body="Test",
                content_type="plain"
            )

            assert "No recipient email specified" in result

    @patch("src.agent.tools.email.smtplib.SMTP")
    @patch("src.agent.tools.email.format_newsletter")
    def test_send_newsletter_success(self, mock_format_newsletter, mock_smtp, email_tools):
        """Test sending newsletter with valid JSON findings"""
        mock_format_newsletter.return_value = "<html>Newsletter</html>"
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        findings = [
            {
                "topic": "Test Topic",
                "summary": "Test summary",
                "sources": ["https://example.com"],
                "tags": ["test"]
            }
        ]

        result = email_tools.send_newsletter(json.dumps(findings))

        assert "Email sent successfully" in result
        mock_format_newsletter.assert_called_once()

    @patch("src.agent.tools.email.smtplib.SMTP")
    @patch("src.agent.tools.email.format_newsletter")
    def test_send_newsletter_invalid_json(self, mock_format_newsletter, mock_smtp, email_tools):
        """Test newsletter handles invalid JSON gracefully"""
        mock_format_newsletter.return_value = "<html>Newsletter</html>"
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Send plain text instead of JSON
        result = email_tools.send_newsletter("Just some text, not JSON")

        # Should still work by treating it as a simple summary
        assert "Email sent successfully" in result

    @patch("src.agent.tools.email.smtplib.SMTP")
    def test_send_simple_email(self, mock_smtp, email_tools):
        """Test sending simple text email"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = email_tools.send_simple_email("Test content")

        assert "Email sent successfully" in result

    def test_get_tools_returns_list(self, email_tools):
        """Test get_tools returns a list of Tool objects"""
        tools = email_tools.get_tools()

        assert isinstance(tools, list)
        assert len(tools) == 2  # send_newsletter, send_email
        assert all(hasattr(tool, "name") for tool in tools)
        assert all(hasattr(tool, "func") for tool in tools)

    def test_create_email_tools_convenience_function(self):
        """Test create_email_tools convenience function"""
        with patch("src.agent.tools.email.config") as mock_config:
            mock_config.SMTP_HOST = "smtp.example.com"
            mock_config.SMTP_PORT = 587
            mock_config.SMTP_USERNAME = "test@example.com"
            mock_config.SMTP_PASSWORD = "password"
            mock_config.SMTP_FROM_EMAIL = "test@example.com"
            mock_config.SMTP_TO_EMAIL = "recipient@example.com"
            mock_config.SMTP_USE_TLS = True

            tools = create_email_tools()

            assert isinstance(tools, list)
            assert len(tools) == 2


class TestMemoryTools:
    """Tests for MemoryTools class"""

    @pytest.fixture
    def mock_memory_service(self):
        """Mock memory service"""
        with patch("src.agent.tools.memory.MemoryService") as mock:
            yield mock

    @pytest.fixture
    def memory_tools(self, mock_memory_service):
        """Create MemoryTools instance with mocked memory service"""
        tools = MemoryTools()
        return tools

    def test_search_memory_success(self, memory_tools):
        """Test successful memory search"""
        # Create mock topic objects
        mock_topic = Mock()
        mock_topic.topic_name = "LangChain"
        mock_topic.summary = "Framework for LLM applications"
        mock_topic.first_researched = datetime(2024, 1, 1)
        mock_topic.sources = ["https://langchain.com"]
        mock_topic.tags = ["framework"]
        mock_topic.last_mentioned = datetime(2024, 1, 1)

        memory_tools.memory_service.search_topics.return_value = [mock_topic]

        result = memory_tools.search_memory("langchain")

        assert "Found 1 topic(s) matching 'langchain'" in result
        assert "LangChain" in result
        assert "Framework for LLM applications" in result

    def test_search_memory_no_results(self, memory_tools):
        """Test memory search with no results"""
        memory_tools.memory_service.search_topics.return_value = []

        result = memory_tools.search_memory("nonexistent")

        assert "No topics found" in result

    def test_search_memory_error(self, memory_tools):
        """Test memory search handles errors"""
        memory_tools.memory_service.search_topics.side_effect = Exception("DB Error")

        # The search_memory method doesn't have error handling currently,
        # so this will raise an exception
        with pytest.raises(Exception):
            memory_tools.search_memory("test")

    def test_check_novelty_new_topic(self, memory_tools):
        """Test checking novelty for new topic"""
        memory_tools.memory_service.is_novel.return_value = True
        memory_tools.memory_service.get_topic_by_name.return_value = None

        result = memory_tools.check_novelty("New Topic")

        assert "NOVEL" in result
        assert "never researched before" in result

    def test_check_novelty_existing_topic(self, memory_tools):
        """Test checking novelty for existing topic"""
        mock_topic = Mock()
        mock_topic.topic_name = "Existing Topic"
        mock_topic.first_researched = datetime(2024, 1, 1)
        mock_topic.last_mentioned = datetime(2024, 1, 15)
        mock_topic.summary = "Previous summary"

        memory_tools.memory_service.is_novel.return_value = False
        memory_tools.memory_service.get_topic_by_name.return_value = mock_topic

        result = memory_tools.check_novelty("Existing Topic")

        assert "NOT novel" in result
        assert "Last mentioned" in result

    def test_get_tools_returns_list(self, memory_tools):
        """Test get_tools returns a list of Tool objects"""
        tools = memory_tools.get_tools()

        assert isinstance(tools, list)
        assert len(tools) == 4  # check_memory, search_memory, check_novelty, memory_stats
        assert all(hasattr(tool, "name") for tool in tools)

    def test_create_memory_tools_convenience_function(self, mock_memory_service):
        """Test create_memory_tools convenience function"""
        tools = create_memory_tools()

        assert isinstance(tools, list)
        assert len(tools) == 4


class TestToolsIntegration:
    """Integration tests for all tools together"""

    @patch("src.agent.tools.search.config")
    @patch("src.agent.tools.search.TavilyClient")
    def test_all_tools_can_be_created(self, mock_tavily, mock_config):
        """Test that all tool sets can be created together"""
        mock_config.TAVILY_API_KEY = "test_key"

        # Create all tool sets
        search_tools = create_search_tools()

        with patch("src.agent.tools.email.config") as email_config:
            email_config.SMTP_HOST = "smtp.example.com"
            email_config.SMTP_USERNAME = "test@example.com"
            email_config.SMTP_PASSWORD = "pass"
            email_tools = create_email_tools()

        memory_tools = create_memory_tools()

        # Verify all were created
        assert len(search_tools) == 4
        assert len(email_tools) == 2
        assert len(memory_tools) == 4

        # Verify total tool count
        all_tools = search_tools + email_tools + memory_tools
        assert len(all_tools) == 10

    def test_tool_names_are_unique(self):
        """Test that all tool names are unique"""
        with patch("src.agent.tools.search.config") as search_config:
            search_config.TAVILY_API_KEY = "test_key"
            with patch("src.agent.tools.search.TavilyClient"):
                search_tools = create_search_tools()

        with patch("src.agent.tools.email.config") as email_config:
            email_config.SMTP_HOST = "smtp.example.com"
            email_config.SMTP_USERNAME = "test@example.com"
            email_config.SMTP_PASSWORD = "pass"
            email_tools = create_email_tools()

        memory_tools = create_memory_tools()

        all_tools = search_tools + email_tools + memory_tools
        tool_names = [tool.name for tool in all_tools]

        # Check uniqueness
        assert len(tool_names) == len(set(tool_names))
