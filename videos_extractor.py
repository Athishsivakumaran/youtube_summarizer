from typing import List, Dict, Optional
from datetime import datetime, timedelta
import os, json, pytz, yt_dlp, config



class YouTubeChannelExtractor:
    def __init__(self):
        """Initialize the YouTube channel extractor with config"""
        self.config = config
        self.logger = self.config.LOGGER


    def _parse_timestamp(self, timestamp: Optional[str]) -> Optional[datetime]:
        """Parse timestamp from various possible formats"""
        if not timestamp:
            return None
        
        try:
            if isinstance(timestamp, str):
                timestamp = timestamp.replace('Z', '+00:00')
                parsed_time = datetime.fromisoformat(timestamp)
            else:
                parsed_time = datetime.fromtimestamp(timestamp, pytz.utc)
            
            return parsed_time if parsed_time.tzinfo else parsed_time.replace(tzinfo=pytz.utc)
        except Exception as e:
            self.logger.warning(f"Could not parse timestamp {timestamp}: {e}")
            return None

    def get_videos_within_timeframe(self, channel_url: str) -> List[Dict]:
        """Fetch videos uploaded within specified time range"""
        # Merge default and custom yt-dlp options
        ydl_opts = {
            'quiet': True,
            'extract_flat': False,
            'playlistend': self.config.MAX_VIDEOS,
            'ignoreerrors': True
        }
        
        videos_in_timeframe = []
        current_time = datetime.now(pytz.utc)
        time_ago = current_time - timedelta(hours=self.config.TIME_RANGE)
        
        try:
            if not channel_url.endswith('/videos'):
                channel_url += '/videos'
            video_fields=["id","title","upload_time"]
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(channel_url, download=False)
                
                entries = info.get('entries', []) or info.get('items', [])
       
                for entry in entries:

                    try:
                        timestamp = (
                            entry.get('timestamp') or 
                            entry.get('upload_date') or 
                            entry.get('published_at')
                        )
                        
                        video_datetime = self._parse_timestamp(timestamp)
                        
                        if not video_datetime:
                            continue
                        
                        if time_ago <= video_datetime <= current_time:
                            video_info = {
                                field: entry.get(field) 
                                for field in video_fields 
                                if field in entry
                            }
                            video_info['upload_time'] = video_datetime.isoformat()
                            
                            videos_in_timeframe.append(video_info)
                    
                    except Exception as video_error:
                        self.logger.error(f"Error processing a video: {video_error}")
        
        except Exception as e:
            self.logger.error(f"Error fetching videos from {channel_url}: {e}")
        
        return videos_in_timeframe

    def extract_channel_videos(self) -> List[Dict]:
        """Extract videos for multiple channels"""
        # Use channels from config if not provided
        channels_to_process=[]
        
        try:
            with open('channels.txt', 'r') as file:
                channels_to_process = [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            self.logger.error("No channels specified and channels.txt not found.")
            return []
        
        all_channel_videos = []
        
        for channel in channels_to_process:
            channel_url = channel if channel.startswith('http') else f"https://www.youtube.com/@{channel}"
            
            videos = self.get_videos_within_timeframe(channel_url)
            print(f"Videos have been processed for channel {channel} . Number of recent videos {len(videos)}")
            all_channel_videos.append({
                'channel_name': channel,
                'videos': videos
            })
        
        return all_channel_videos

    def save_to_json(self, data: List[Dict], filename: str = None):
        """Save extracted data to JSON file"""
        
        filepath =self.config.EXTRACTED_VIDEOS_FILE
        
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            
            self.logger.info(f"Saved videos to {filepath}")
        except Exception as e:
            self.logger.error(f"Error saving to JSON: {e}")

def VideoExtractor():
    """Main entry point for the script"""
    extractor = YouTubeChannelExtractor()
    
    try:
        # Extract videos
        extracted_data = extractor.extract_channel_videos()
        
        # Save to JSON
        extractor.save_to_json(extracted_data)
    
    except Exception as e:
        self.logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()