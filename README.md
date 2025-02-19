# YouTube Video Summarizer 📺 ➡️ 📧

## Overview 🎯
A smart tool that automatically fetches, summarizes, and emails you content from your favorite YouTube channels. Save time, stay informed, and maintain focus by receiving key insights directly in your inbox.

## Key Benefits 💡
- Extract valuable insights without watching full videos
- Avoid falling into recommendation rabbit holes
- Save hours of watching time
- Stay updated with multiple channels efficiently
- Process information in text format for better retention

## Features ✨
- 🎯 Automated channel monitoring
- 📑 Chapter-based video summaries
- 🤖 AI-powered content extraction using Ollama
- 📧 Direct email delivery of summaries
- ⏰ 12-hour update intervals
- 🔄 Continuous background processing

## Setup 🛠️

### Prerequisites
- Python 3.8+
- Ollama installed locally
- Gmail account with App Password

### Installation
```bash
git clone https://github.com/yourusername/youtube-summarizer.git
cd youtube-summarizer
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
ollama pull mistral
```

### Configuration
Update `config.py` with your settings:
```python
# Output settings
OUTPUT_DIR = "IO_FILES"
TIME_RANGE = 24  # Hours
MAX_VIDEOS = 3   # Per channel

# Email settings
EMAIL_SENDER = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 587
NUMBERS = ["recipient1@gmail.com", "recipient2@gmail.com"]
```

Add channels to `channels.txt`:
```
@channelname1
@channelname2
```

## Automation Setup 🔄

### macOS
```bash
# Schedule wake-ups
sudo pmset repeat wakeorpoweron MTWRFSU 00:00,12:00

# Create Launch Agent
mkdir -p ~/Library/LaunchAgents
cat << EOF > ~/Library/LaunchAgents/com.youtube.summarizer.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>com.youtube.summarizer</string>
    <key>ProgramArguments</key>
    <array>
      <string>/Users/YOUR_USERNAME/youtube-summarizer/venv/bin/python</string>
      <string>/Users/YOUR_USERNAME/youtube-summarizer/main.py</string>
    </array>
    <key>StartInterval</key>
    <integer>43200</integer>
    <key>RunAtLoad</key>
    <true/>
  </dict>
</plist>
EOF

# Load service
launchctl load ~/Library/LaunchAgents/com.youtube.summarizer.plist
```

### Windows
1. Create `run_summarizer.bat`:
```batch
@echo off
cd /d "C:\Path\To\youtube-summarizer"
call venv\Scripts\activate.bat
python main.py
```

2. Set up Task Scheduler:
- Open Task Scheduler
- Create Basic Task
- Trigger: Daily, repeat every 12 hours
- Action: Start Program -> `run_summarizer.bat`
- Check "Run with highest privileges"

## Usage 🚀
Manual run:
```bash
python main.py
```

## Project Structure 📁
```
youtube_summariser/
├── IO_FILES/           # Generated files
├── config.py          # Settings
├── main.py           # Entry point
├── messages_sender.py # Email service
├── text_summarizer.py # AI processing
├── transcript_extractor.py
├── videos_extractor.py
└── requirements.txt
```

## Support
- Create issues on GitHub for bugs
- Check documentation for common issues
- Contact maintainers for help

---
Made with ❤️ by Athish Sivakumaran
