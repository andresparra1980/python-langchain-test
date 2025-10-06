import logging
from typing import Optional, Dict, Any
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from src.adapters.base import InputAdapter
from config import config


# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramAdapter(InputAdapter):
    """
    Telegram bot adapter for messaging-based interaction.

    Provides a Telegram bot interface for interacting with the agent.
    Supports commands, message handling, and Telegram-specific formatting.
    """

    def __init__(self, agent_core=None, bot_token: Optional[str] = None):
        """
        Initialize the Telegram adapter.

        Args:
            agent_core: The agent core instance to process messages
            bot_token: Telegram bot token (defaults to config.TELEGRAM_BOT_TOKEN)
        """
        super().__init__(agent_core)
        self.bot_token = bot_token or config.TELEGRAM_BOT_TOKEN

        if not self.bot_token:
            raise ValueError(
                "Telegram bot token not provided. "
                "Set TELEGRAM_BOT_TOKEN in your .env file or pass it to the constructor."
            )

        self.application: Optional[Application] = None
        self.user_sessions: Dict[int, Dict[str, Any]] = {}

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle the /start command.

        Args:
            update: The Telegram update object
            context: The callback context
        """
        user = update.effective_user
        logger.info(f"User {user.id} ({user.username}) started the bot")

        welcome_message = (
            f"👋 Hi {user.first_name}!\n\n"
            "I'm your AI Research Assistant. I can help you:\n"
            "• Research trending AI topics and technologies\n"
            "• Search for papers, libraries, and frameworks\n"
            "• Remember our conversations to avoid repetition\n"
            "• Send newsletter summaries via email\n\n"
            "Just send me a message to get started!\n\n"
            "Commands:\n"
            "/start - Show this welcome message\n"
            "/help - Get help\n"
            "/clear - Clear conversation history\n"
            "/stats - Show memory statistics"
        )

        await update.message.reply_text(welcome_message)

    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle the /help command.

        Args:
            update: The Telegram update object
            context: The callback context
        """
        help_message = (
            "🤖 *AI Research Assistant Help*\n\n"
            "*Available Commands:*\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/clear - Clear conversation history\n"
            "/stats - Show memory statistics\n\n"
            "*Example Queries:*\n"
            "• Research new Python AI libraries\n"
            "• Search for papers about transformers\n"
            "• What did we discuss about LangChain?\n"
            "• Send me a newsletter with recent findings\n\n"
            "Just send me a message and I'll help you research AI topics!"
        )

        await update.message.reply_text(help_message, parse_mode="Markdown")

    async def _clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle the /clear command.

        Args:
            update: The Telegram update object
            context: The callback context
        """
        user_id = update.effective_user.id

        # Clear session data for this user
        if user_id in self.user_sessions:
            self.user_sessions[user_id].clear()

        await update.message.reply_text("✅ Conversation history cleared!")

    async def _stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle the /stats command.

        Args:
            update: The Telegram update object
            context: The callback context
        """
        # This would integrate with the memory system to show stats
        # For now, show placeholder message
        stats_message = (
            "📊 *Memory Statistics*\n\n"
            "Use the agent to get detailed statistics by asking:\n"
            "\"Show me memory statistics\""
        )

        await update.message.reply_text(stats_message, parse_mode="Markdown")

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle incoming text messages.

        Args:
            update: The Telegram update object
            context: The callback context
        """
        user = update.effective_user
        user_id = user.id
        message_text = update.message.text

        logger.info(f"Received message from {user.username} ({user_id}): {message_text}")

        # Initialize user session if needed
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {}

        # Show typing indicator
        await update.message.chat.send_action(action="typing")

        try:
            # Process message through agent (async version)
            if self.agent_core:
                # Reset tool call counter for this message
                # Each user message gets a fresh limit
                if hasattr(self.agent_core, 'reset_tool_call_count'):
                    self.agent_core.reset_tool_call_count()

                result = await self.agent_core.arun(message_text)

                # Extract output from result dictionary
                if isinstance(result, dict):
                    response = result.get("output", str(result))
                else:
                    response = str(result)

                # Format response for this channel
                response = self.format_response(response)
            else:
                response = None

            if response:
                # Send response (Telegram has a 4096 character limit)
                await self._send_long_message(update, response)
            else:
                await update.message.reply_text(
                    "❌ Sorry, I couldn't process your message. Please try again."
                )

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            await update.message.reply_text(
                f"❌ An error occurred: {str(e)}\n\nPlease try again or rephrase your query."
            )

    async def _send_long_message(self, update: Update, message: str) -> None:
        """
        Send a long message, splitting if necessary to respect Telegram's limits.

        Args:
            update: The Telegram update object
            message: The message to send
        """
        max_length = 4096

        if len(message) <= max_length:
            await update.message.reply_text(message)
        else:
            # Split message into chunks
            chunks = []
            current_chunk = ""

            for line in message.split("\n"):
                if len(current_chunk) + len(line) + 1 > max_length:
                    chunks.append(current_chunk)
                    current_chunk = line
                else:
                    if current_chunk:
                        current_chunk += "\n" + line
                    else:
                        current_chunk = line

            if current_chunk:
                chunks.append(current_chunk)

            # Send chunks
            for i, chunk in enumerate(chunks):
                if i == 0:
                    await update.message.reply_text(chunk)
                else:
                    await update.message.reply_text(f"(continued...)\n\n{chunk}")

    async def _error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle errors in the bot.

        Args:
            update: The Telegram update object
            context: The callback context
        """
        logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)

    def start(self) -> None:
        """
        Start the Telegram bot.

        This method starts the bot using polling mode. For production,
        you may want to use webhooks instead.
        """
        logger.info("Starting Telegram bot...")

        # Create application
        self.application = Application.builder().token(self.bot_token).build()

        # Register handlers
        self.application.add_handler(CommandHandler("start", self._start_command))
        self.application.add_handler(CommandHandler("help", self._help_command))
        self.application.add_handler(CommandHandler("clear", self._clear_command))
        self.application.add_handler(CommandHandler("stats", self._stats_command))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message)
        )

        # Register error handler
        self.application.add_error_handler(self._error_handler)

        # Start polling
        logger.info("Bot is running. Press Ctrl+C to stop.")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

    def stop(self) -> None:
        """
        Stop the Telegram bot.

        Performs cleanup and stops the application.
        """
        if self.application:
            logger.info("Stopping Telegram bot...")
            # The application will be stopped by the run_polling context manager

    def receive_message(self) -> Optional[str]:
        """
        Receive a message from Telegram.

        This method is not used in the async bot implementation.
        Messages are received through the message handler.

        Returns:
            None (not applicable for async bot)
        """
        # Not applicable for async Telegram bot
        return None

    def send_message(self, message: str) -> bool:
        """
        Send a message through Telegram.

        This method is not used in the async bot implementation.
        Messages are sent through the update context.

        Args:
            message: The message to send

        Returns:
            False (not applicable for async bot)
        """
        # Not applicable for async Telegram bot
        # Messages are sent through the update context in _handle_message
        return False

    def format_response(self, response: str) -> str:
        """
        Format a response for Telegram.

        Applies Telegram-specific formatting and escaping.

        Args:
            response: The raw response from the agent

        Returns:
            Formatted response for Telegram
        """
        # For now, keep it simple
        # Could add markdown formatting or emoji enhancements here
        return response
