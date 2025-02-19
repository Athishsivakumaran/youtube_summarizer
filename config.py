import os, logging
from typing import List, Optional


OUTPUT_DIR: str = "IO_FILES"

# Time range for video extraction (hours)
TIME_RANGE: int = 24

# Maximum number of videos to extract per channel
MAX_VIDEOS: int = 3

# Output directory for saved files
EXTRACTED_VIDEOS_FILE: str = OUTPUT_DIR + "/extracted_channel_videos.json"


# Configure logging
logging.basicConfig(
    level=getattr(logging, 'INFO',),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(OUTPUT_DIR+'/youtube_video_extraction.log'),
        logging.StreamHandler()
    ]
)

CHUNK_SIZE:int =  10000

LOGGER = logging.getLogger(__name__)

SUBTITLE_LANGS: list = ['en', 'en-US', 'en-GB']

VIDEO_TRANSCRIPT_FILE: str = OUTPUT_DIR + '/video_transcripts.json'

SUMMARIZED_TRANSCRIPT_FILE: str = OUTPUT_DIR + '/summarized_transcripts.json'

OLLAMA_MODEL: str = "mistral:latest"

OLLAMA_URL: str = "http://localhost:11434/api/generate"

VTT_FILES: str = OUTPUT_DIR + "/vtt_files"


EMAIL_SENDER = "athishsivakumaran@gmail.com"
EMAIL_PASSWORD = "adfv yhlf jnik ntfw"
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 587
NUMBERS = ["athishsivakumaran@gmail.com", "71762133006@cit.edu.in"]  # Email addresses
