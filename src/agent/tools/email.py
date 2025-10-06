import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain.tools import Tool

from config import config
from src.utils.formatters import format_newsletter


class EmailTools:
    """LangChain tools for sending emails"""

    def __init__(self):
        """Initialize email tools with SMTP configuration"""
        self.smtp_host = config.SMTP_HOST
        self.smtp_port = config.SMTP_PORT
        self.smtp_username = config.SMTP_USERNAME
        self.smtp_password = config.SMTP_PASSWORD
        self.smtp_from_email = config.SMTP_FROM_EMAIL or config.SMTP_USERNAME
        self.smtp_to_email = config.SMTP_TO_EMAIL
        self.smtp_use_tls = config.SMTP_USE_TLS

    def _validate_config(self) -> bool:
        """
        Validate that required email configuration is present.

        Returns:
            True if configuration is valid

        Raises:
            ValueError if required configuration is missing
        """
        required_fields = {
            "SMTP_HOST": self.smtp_host,
            "SMTP_USERNAME": self.smtp_username,
            "SMTP_PASSWORD": self.smtp_password,
        }

        missing = [name for name, value in required_fields.items() if not value]

        if missing:
            raise ValueError(
                f"Missing required email configuration: {', '.join(missing)}. "
                "Please check your .env file."
            )

        return True

    def _send_email(
        self,
        subject: str,
        body: str,
        to_email: Optional[str] = None,
        content_type: str = "html"
    ) -> str:
        """
        Send an email via SMTP.

        Args:
            subject: Email subject
            body: Email body content
            to_email: Recipient email (defaults to config.SMTP_TO_EMAIL)
            content_type: Content type ('html' or 'plain')

        Returns:
            Success or error message
        """
        try:
            # Validate configuration
            self._validate_config()

            # Determine recipient
            recipient = to_email or self.smtp_to_email
            if not recipient:
                raise ValueError(
                    "No recipient email specified. Please set SMTP_TO_EMAIL in config or provide to_email."
                )

            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.smtp_from_email
            msg["To"] = recipient
            msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

            # Attach body
            mime_subtype = "html" if content_type == "html" else "plain"
            msg.attach(MIMEText(body, mime_subtype, "utf-8"))

            # Connect to SMTP server
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
                if self.smtp_use_tls:
                    server.starttls()

                # Login if credentials provided
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)

                # Send email
                server.send_message(msg)

            return f"Email sent successfully to {recipient}"

        except smtplib.SMTPAuthenticationError as e:
            return f"Email authentication failed: {str(e)}. Please check SMTP credentials."
        except smtplib.SMTPConnectError as e:
            return f"Failed to connect to SMTP server: {str(e)}. Please check SMTP_HOST and SMTP_PORT."
        except smtplib.SMTPException as e:
            return f"SMTP error occurred: {str(e)}"
        except ValueError as e:
            return f"Configuration error: {str(e)}"
        except Exception as e:
            return f"Error sending email: {str(e)}"

    def send_newsletter(self, findings_json: str) -> str:
        """
        Send a newsletter email with research findings.

        This function expects a JSON string representation of findings.
        The agent should provide findings in this format:
        [
            {
                "topic": "Topic name",
                "summary": "Brief summary",
                "sources": ["url1", "url2"],
                "tags": ["tag1", "tag2"]
            }
        ]

        Args:
            findings_json: JSON string of research findings

        Returns:
            Success or error message
        """
        try:
            import json

            # Parse findings
            try:
                findings = json.loads(findings_json)
            except json.JSONDecodeError:
                # If not valid JSON, treat as a simple text summary
                findings = [{
                    "topic": "Research Summary",
                    "summary": findings_json,
                    "sources": [],
                    "tags": []
                }]

            # Ensure findings is a list
            if not isinstance(findings, list):
                findings = [findings]

            # Generate newsletter
            date_str = datetime.now().strftime("%B %d, %Y")
            subject = config.NEWSLETTER_SUBJECT.format(date=date_str)

            # Format based on configured format
            newsletter_format = config.NEWSLETTER_FORMAT.lower()
            content_type = "html" if newsletter_format == "html" else "plain"

            body = format_newsletter(
                findings=findings,
                format_type=newsletter_format,
                introduction="Here are the latest AI research findings."
            )

            # Send email
            result = self._send_email(
                subject=subject,
                body=body,
                content_type=content_type
            )

            return result

        except Exception as e:
            return f"Error generating newsletter: {str(e)}"

    def send_simple_email(self, content: str) -> str:
        """
        Send a simple text email with the provided content.

        Args:
            content: Email content

        Returns:
            Success or error message
        """
        try:
            subject = f"Research Assistant Update - {datetime.now().strftime('%Y-%m-%d')}"

            result = self._send_email(
                subject=subject,
                body=content,
                content_type="plain"
            )

            return result

        except Exception as e:
            return f"Error sending email: {str(e)}"

    def get_tools(self) -> List[Tool]:
        """
        Get LangChain tools for email operations.

        Returns:
            List of LangChain Tool objects
        """
        return [
            Tool(
                name="send_newsletter",
                func=self.send_newsletter,
                description=(
                    "Send a newsletter email with research findings. "
                    "IMPORTANT: First use search_memory to get recent topics, then pass them here. "
                    "Input MUST be a valid JSON string (use json.dumps) with this exact structure: "
                    '[{"topic": "Topic Name", "summary": "Detailed summary of findings", "sources": ["https://url1.com", "https://url2.com"], "tags": ["tag1", "tag2"]}]. '
                    "Each topic should have: topic (string), summary (string, be detailed!), sources (list of URLs), tags (list). "
                    "Make sure summaries are comprehensive - include key details, features, or findings. "
                    "Use this when the user explicitly requests a newsletter or email report."
                )
            ),
            Tool(
                name="send_email",
                func=self.send_simple_email,
                description=(
                    "Send a simple text email with the provided content. "
                    "Input should be the email content as a string. "
                    "Use this for sending quick updates or simple messages. "
                    "For research findings, prefer using send_newsletter instead."
                )
            ),
        ]


def create_email_tools() -> List[Tool]:
    """
    Convenience function to create email tools.

    Returns:
        List of LangChain Tool objects for email operations
    """
    email_tools = EmailTools()
    return email_tools.get_tools()
