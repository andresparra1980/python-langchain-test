"""Unit tests for input adapters"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call, AsyncMock
import sys
from io import StringIO

from src.adapters.base import InputAdapter
from src.adapters.cli import CLIAdapter
from src.adapters.telegram import TelegramAdapter


class ConcreteAdapter(InputAdapter):
    """Concrete implementation of InputAdapter for testing"""

    def start(self):
        pass

    def stop(self):
        pass

    def receive_message(self):
        return "test message"

    def send_message(self, message):
        return True


class TestInputAdapter:
    """Tests for the base InputAdapter class"""

    @pytest.fixture
    def adapter(self):
        """Create a concrete adapter instance for testing"""
        return ConcreteAdapter()

    def test_initialization(self, adapter):
        """Test adapter initializes with default values"""
        assert adapter.agent_core is None
        assert adapter.session_data == {}

    def test_initialization_with_agent(self):
        """Test adapter initializes with agent core"""
        mock_agent = Mock()
        adapter = ConcreteAdapter(agent_core=mock_agent)
        assert adapter.agent_core == mock_agent

    def test_format_response_default(self, adapter):
        """Test default format_response returns input unchanged"""
        response = "test response"
        assert adapter.format_response(response) == response

    def test_process_message_no_agent(self, adapter):
        """Test process_message returns error when no agent configured"""
        result = adapter.process_message("test")
        assert "No agent core configured" in result

    def test_process_message_success(self):
        """Test process_message with successful agent response"""
        mock_agent = Mock()
        mock_agent.run.return_value = {"output": "Agent response"}

        adapter = ConcreteAdapter(agent_core=mock_agent)
        result = adapter.process_message("test query")

        assert result == "Agent response"
        mock_agent.run.assert_called_once_with("test query")

    def test_process_message_dict_response(self):
        """Test process_message handles dict response correctly"""
        mock_agent = Mock()
        mock_agent.run.return_value = {
            "output": "Response text",
            "success": True,
            "tool_calls": 3
        }

        adapter = ConcreteAdapter(agent_core=mock_agent)
        result = adapter.process_message("test")

        assert result == "Response text"

    def test_process_message_string_response(self):
        """Test process_message handles string response"""
        mock_agent = Mock()
        mock_agent.run.return_value = "Direct string response"

        adapter = ConcreteAdapter(agent_core=mock_agent)
        result = adapter.process_message("test")

        assert result == "Direct string response"

    def test_process_message_error(self):
        """Test process_message handles errors gracefully"""
        mock_agent = Mock()
        mock_agent.run.side_effect = Exception("Test error")

        adapter = ConcreteAdapter(agent_core=mock_agent)
        result = adapter.process_message("test")

        assert "Error processing message" in result
        assert "Test error" in result

    def test_session_data_get_set(self, adapter):
        """Test session data get/set operations"""
        adapter.set_session_data("key1", "value1")
        assert adapter.get_session_data("key1") == "value1"

    def test_session_data_get_default(self, adapter):
        """Test session data returns default for missing key"""
        assert adapter.get_session_data("nonexistent", "default") == "default"

    def test_session_data_clear(self, adapter):
        """Test clearing session data"""
        adapter.set_session_data("key1", "value1")
        adapter.set_session_data("key2", "value2")

        adapter.clear_session_data()

        assert adapter.session_data == {}


class TestCLIAdapter:
    """Tests for CLIAdapter"""

    @pytest.fixture
    def cli_adapter(self):
        """Create a CLI adapter for testing"""
        mock_agent = Mock()
        return CLIAdapter(agent_core=mock_agent, prompt="Test> ")

    def test_initialization(self, cli_adapter):
        """Test CLI adapter initializes correctly"""
        assert cli_adapter.prompt == "Test> "
        assert cli_adapter.running is False

    def test_check_color_support(self, cli_adapter):
        """Test color support detection"""
        # This will vary based on environment, just test it doesn't error
        result = cli_adapter._check_color_support()
        assert isinstance(result, bool)

    def test_colorize_with_colors(self):
        """Test colorize with colors enabled"""
        adapter = CLIAdapter()
        adapter.use_colors = True

        result = adapter._colorize("test", "blue")

        assert "test" in result
        # Should contain ANSI codes
        assert "\033[" in result

    def test_colorize_without_colors(self):
        """Test colorize with colors disabled"""
        adapter = CLIAdapter()
        adapter.use_colors = False

        result = adapter._colorize("test", "blue")

        assert result == "test"
        # Should not contain ANSI codes
        assert "\033[" not in result

    @patch("builtins.input", side_effect=["exit"])
    @patch("sys.stdout", new_callable=StringIO)
    def test_start_and_exit(self, mock_stdout, mock_input, cli_adapter):
        """Test starting CLI and exiting"""
        cli_adapter.start()

        assert cli_adapter.running is False
        output = mock_stdout.getvalue()
        assert "Goodbye" in output or "Welcome" in output

    @patch("builtins.input", side_effect=["help", "exit"])
    @patch("sys.stdout", new_callable=StringIO)
    def test_help_command(self, mock_stdout, mock_input, cli_adapter):
        """Test help command"""
        cli_adapter.start()

        output = mock_stdout.getvalue()
        assert "Available commands" in output or "help" in output.lower()

    @patch("builtins.input", side_effect=["clear", "exit"])
    @patch("sys.stdout", new_callable=StringIO)
    def test_clear_command(self, mock_stdout, mock_input, cli_adapter):
        """Test clear command"""
        cli_adapter.set_session_data("test", "data")
        cli_adapter.start()

        assert cli_adapter.session_data == {}

    @patch("builtins.input", side_effect=["test message", "exit"])
    @patch("sys.stdout", new_callable=StringIO)
    def test_message_processing(self, mock_stdout, mock_input, cli_adapter):
        """Test processing a message through the CLI"""
        cli_adapter.agent_core.run.return_value = {"output": "Agent response"}

        cli_adapter.start()

        cli_adapter.agent_core.run.assert_called()
        output = mock_stdout.getvalue()
        assert "Agent response" in output

    @patch("builtins.input", side_effect=EOFError())
    @patch("sys.stdout", new_callable=StringIO)
    def test_eof_handling(self, mock_stdout, mock_input, cli_adapter):
        """Test handling of Ctrl+D (EOF)"""
        cli_adapter.start()

        assert cli_adapter.running is False

    @patch("builtins.input", side_effect=KeyboardInterrupt())
    @patch("sys.stdout", new_callable=StringIO)
    def test_keyboard_interrupt_handling(self, mock_stdout, mock_input, cli_adapter):
        """Test handling of Ctrl+C (KeyboardInterrupt)"""
        cli_adapter.start()

        assert cli_adapter.running is False

    def test_receive_message(self, cli_adapter):
        """Test receive_message method"""
        with patch("builtins.input", return_value="test input"):
            result = cli_adapter.receive_message()
            assert result == "test input"

    def test_receive_message_cancelled(self, cli_adapter):
        """Test receive_message with cancellation"""
        with patch("builtins.input", side_effect=EOFError()):
            result = cli_adapter.receive_message()
            assert result is None

    @patch("sys.stdout", new_callable=StringIO)
    def test_send_message(self, mock_stdout, cli_adapter):
        """Test send_message method"""
        result = cli_adapter.send_message("Test message")

        assert result is True
        output = mock_stdout.getvalue()
        assert "Test message" in output

    def test_format_response(self, cli_adapter):
        """Test format_response for CLI"""
        response = "Test response"
        result = cli_adapter.format_response(response)
        assert result == response

    def test_stop(self, cli_adapter):
        """Test stop method"""
        cli_adapter.running = True
        cli_adapter.stop()
        assert cli_adapter.running is False


class TestTelegramAdapter:
    """Tests for TelegramAdapter"""

    @pytest.fixture
    def telegram_adapter(self):
        """Create a Telegram adapter for testing"""
        mock_agent = Mock()
        with patch("src.adapters.telegram.config") as mock_config:
            mock_config.TELEGRAM_BOT_TOKEN = "test_token"
            return TelegramAdapter(agent_core=mock_agent, bot_token="test_token")

    def test_initialization_with_token(self):
        """Test Telegram adapter initializes with token"""
        mock_agent = Mock()
        adapter = TelegramAdapter(agent_core=mock_agent, bot_token="test_token")
        assert adapter.bot_token == "test_token"

    def test_initialization_from_config(self):
        """Test Telegram adapter gets token from config"""
        with patch("src.adapters.telegram.config") as mock_config:
            mock_config.TELEGRAM_BOT_TOKEN = "config_token"
            adapter = TelegramAdapter()
            assert adapter.bot_token == "config_token"

    def test_initialization_no_token(self):
        """Test Telegram adapter raises error without token"""
        with patch("src.adapters.telegram.config") as mock_config:
            mock_config.TELEGRAM_BOT_TOKEN = None
            with pytest.raises(ValueError, match="Telegram bot token not provided"):
                TelegramAdapter()

    @pytest.mark.asyncio
    async def test_start_command(self, telegram_adapter):
        """Test /start command handler"""
        mock_update = Mock()
        mock_update.effective_user.id = 12345
        mock_update.effective_user.username = "testuser"
        mock_update.effective_user.first_name = "Test"
        mock_update.message.reply_text = AsyncMock()

        await telegram_adapter._start_command(mock_update, Mock())

        mock_update.message.reply_text.assert_called_once()
        args = mock_update.message.reply_text.call_args[0]
        assert "Hi Test" in args[0]

    @pytest.mark.asyncio
    async def test_help_command(self, telegram_adapter):
        """Test /help command handler"""
        mock_update = Mock()
        mock_update.message.reply_text = AsyncMock()

        await telegram_adapter._help_command(mock_update, Mock())

        mock_update.message.reply_text.assert_called_once()
        args, kwargs = mock_update.message.reply_text.call_args
        assert "Help" in args[0]
        assert kwargs.get("parse_mode") == "Markdown"

    @pytest.mark.asyncio
    async def test_clear_command(self, telegram_adapter):
        """Test /clear command handler"""
        mock_update = Mock()
        mock_update.effective_user.id = 12345
        mock_update.message.reply_text = AsyncMock()

        # Add some session data
        telegram_adapter.user_sessions[12345] = {"test": "data"}

        await telegram_adapter._clear_command(mock_update, Mock())

        assert telegram_adapter.user_sessions[12345] == {}
        mock_update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_stats_command(self, telegram_adapter):
        """Test /stats command handler"""
        mock_update = Mock()
        mock_update.message.reply_text = AsyncMock()

        await telegram_adapter._stats_command(mock_update, Mock())

        mock_update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_message_success(self, telegram_adapter):
        """Test message handling with successful response"""
        mock_update = Mock()
        mock_update.effective_user.id = 12345
        mock_update.effective_user.username = "testuser"
        mock_update.message.text = "test query"
        mock_update.message.chat.send_action = AsyncMock()
        mock_update.message.reply_text = AsyncMock()

        telegram_adapter.agent_core.arun = AsyncMock()
        telegram_adapter.agent_core.arun.return_value = {"output": "Agent response"}

        await telegram_adapter._handle_message(mock_update, Mock())

        telegram_adapter.agent_core.arun.assert_called_once_with("test query")
        mock_update.message.reply_text.assert_called()

    @pytest.mark.asyncio
    async def test_handle_message_error(self, telegram_adapter):
        """Test message handling with error"""
        mock_update = Mock()
        mock_update.effective_user.id = 12345
        mock_update.effective_user.username = "testuser"
        mock_update.message.text = "test query"
        mock_update.message.chat.send_action = AsyncMock()
        mock_update.message.reply_text = AsyncMock()

        telegram_adapter.agent_core.arun = AsyncMock()
        telegram_adapter.agent_core.arun.side_effect = Exception("Test error")

        await telegram_adapter._handle_message(mock_update, Mock())

        # Should send error message
        mock_update.message.reply_text.assert_called()
        args = mock_update.message.reply_text.call_args[0]
        assert "error" in args[0].lower()

    @pytest.mark.asyncio
    async def test_send_long_message_short(self, telegram_adapter):
        """Test sending a short message"""
        mock_update = Mock()
        mock_update.message.reply_text = AsyncMock()

        short_message = "Short message"
        await telegram_adapter._send_long_message(mock_update, short_message)

        mock_update.message.reply_text.assert_called_once_with(short_message)

    @pytest.mark.asyncio
    async def test_send_long_message_long(self, telegram_adapter):
        """Test sending a long message that needs splitting"""
        mock_update = Mock()
        mock_update.message.reply_text = AsyncMock()

        # Create a message longer than 4096 characters
        long_message = "A" * 5000
        await telegram_adapter._send_long_message(mock_update, long_message)

        # Should be called multiple times
        assert mock_update.message.reply_text.call_count > 1

    def test_receive_message_not_applicable(self, telegram_adapter):
        """Test receive_message returns None (not applicable for async bot)"""
        result = telegram_adapter.receive_message()
        assert result is None

    def test_send_message_not_applicable(self, telegram_adapter):
        """Test send_message returns False (not applicable for async bot)"""
        result = telegram_adapter.send_message("test")
        assert result is False

    def test_format_response(self, telegram_adapter):
        """Test format_response for Telegram"""
        response = "Test response"
        result = telegram_adapter.format_response(response)
        assert result == response


class TestAdaptersIntegration:
    """Integration tests for adapters"""

    def test_all_adapters_implement_base_interface(self):
        """Test that all adapters implement the base interface"""
        from inspect import ismethod

        required_methods = ["start", "stop", "receive_message", "send_message", "format_response"]

        # Test CLI adapter
        cli = CLIAdapter()
        for method in required_methods:
            assert hasattr(cli, method)
            assert ismethod(getattr(cli, method))

        # Test Telegram adapter
        telegram = TelegramAdapter(bot_token="test_token")
        for method in required_methods:
            assert hasattr(telegram, method)
            assert ismethod(getattr(telegram, method))

    def test_adapter_session_management(self):
        """Test that adapters can manage session data"""
        cli = CLIAdapter()

        # Set and get session data
        cli.set_session_data("user_id", 123)
        cli.set_session_data("preferences", {"theme": "dark"})

        assert cli.get_session_data("user_id") == 123
        assert cli.get_session_data("preferences")["theme"] == "dark"

        # Clear session
        cli.clear_session_data()
        assert cli.get_session_data("user_id") is None
