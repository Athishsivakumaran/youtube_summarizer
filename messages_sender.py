from datetime import datetime
from typing import List, Dict, Optional
import os
import json
import time
import smtplib
from email.message import EmailMessage
import config  # Your configuration file with email settings, JSON file path, etc.

class MessageSender:
    def __init__(self):
        """Initialize message sender with configuration."""
        self.config = config
        self.logger = self.config.LOGGER

    def format_upload_time(self, iso_time: str) -> str:
        """
        Convert ISO timestamp to a readable format.

        Args:
            iso_time (str): ISO formatted timestamp.

        Returns:
            str: Formatted timestamp string.
        """
        try:
            dt = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
            return dt.strftime("%B %d, %Y at %I:%M %p")
        except Exception as e:
            self.logger.error(f"Timestamp formatting error: {e}")
            return iso_time

    def create_channel_html(self, channel: Dict) -> Optional[str]:
        """
        Create an HTML formatted block for a channel if there is video data.
        
        Args:
            channel (Dict): Channel data dictionary.
        
        Returns:
            Optional[str]: HTML block containing channel details, or None if no video data.
        """
        html_parts = []
        channel_name = channel.get('channel_name', 'Unknown Channel')

        for video in channel.get('videos', []):
            if video:
                title = video.get('title', 'No title available')
                upload_time = self.format_upload_time(video.get('upload_time', ''))
                description = video.get('description', 'No description available')

                # Build chapter summaries section.
                chapter_summaries = ""
                if video.get('chapter_summaries'):
                    for chapter, summary in video['chapter_summaries'].items():
                        chapter_summaries += (
                            f"<p style='margin: 0 0 10px 0;'><strong>{chapter}:</strong> {summary}</p>"
                        )
                else:
                    chapter_summaries = "<p>No chapter summaries available</p>"

                video_html = f"""
                <div style="margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #e0e0e0;">
                  <h2 style="color: #333;">Channel: {channel_name}</h2>
                  <h3 style="color: #555;">Title: {title}</h3>
                  <p style="margin: 5px 0;"><strong>Upload Time:</strong> {upload_time}</p>
                  <p style="margin: 5px 0;"><strong>Description:</strong> {description}</p>
                  <h3 style="color: #333; margin-top: 20px;">Chapter Summaries</h3>
                  {chapter_summaries}
                </div>
                """
                html_parts.append(video_html)

        # If no valid video data was found, return None.
        if not html_parts:
            return None

        # Combine all video blocks for this channel.
        return "".join(html_parts)

    def build_full_email_html(self, channels: List[Dict]) -> Optional[str]:
        """
        Combine all channels' HTML blocks into a single email HTML message.
        
        Args:
            channels (List[Dict]): List of channel data dictionaries.
        
        Returns:
            Optional[str]: Full HTML content for the email, or None if no channel has video data.
        """
        combined_html_parts = []
        for channel in channels:
            channel_html = self.create_channel_html(channel)
            if channel_html:
                combined_html_parts.append(channel_html)

        if not combined_html_parts:
            return None

        full_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Channel Video Summary</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; margin: 0;">
  <div style="max-width: 700px; margin: auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);">
    {''.join(combined_html_parts)}
    <p style="text-align: center; color: #888; font-size: 0.9em;">&copy; 2025 Your Company Name</p>
  </div>
</body>
</html>"""
        return full_html

    def send_email_messages(self, recipient_email: str, html_content: str) -> None:
        """
        Send an HTML email with the formatted content.
        
        Args:
            recipient_email (str): Recipient's email address.
            html_content (str): HTML formatted email content.
        """
        try:
            email_message = EmailMessage()
            # Provide a plain text fallback.
            email_message.set_content("Please view this email in an HTML-compatible email viewer.")
            email_message.add_alternative(html_content, subtype='html')
            email_message['Subject'] = 'Channel Video Summary'
            email_message['From'] = self.config.EMAIL_SENDER
            email_message['To'] = recipient_email

            with smtplib.SMTP(self.config.EMAIL_SMTP_SERVER, self.config.EMAIL_SMTP_PORT) as server:
                server.starttls()
                server.login(self.config.EMAIL_SENDER, self.config.EMAIL_PASSWORD)
                server.send_message(email_message)

            # Optional: pause briefly between emails.
            time.sleep(5)
        except Exception as e:
            self.logger.error(f"Email sending error: {e}")

    def process_input_json(self) -> Optional[List[Dict]]:
        """
        Process the input JSON file, build the full HTML email, and send it to each recipient.
        
        Returns:
            Optional[List[Dict]]: Processed JSON data or None if file not found.
        """
        if not os.path.exists(self.config.SUMMARIZED_TRANSCRIPT_FILE):
            self.logger.error(f"Input file not found: {self.config.SUMMARIZED_TRANSCRIPT_FILE}")
            return None

        with open(self.config.SUMMARIZED_TRANSCRIPT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        full_email_html = self.build_full_email_html(data)
        if not full_email_html:
            self.logger.info("No valid channel data found to send an email.")
            return data

        # Send one combined email per recipient.
        for recipient in self.config.NUMBERS:
            self.send_email_messages(recipient, full_email_html)

        self.logger.info("Message sending process completed")
        return data

def MessageSenderProcess():
    """Main entry point for sending emails."""
    sender = MessageSender()
    sender.process_input_json()

if __name__ == "__main__":
    MessageSenderProcess()
