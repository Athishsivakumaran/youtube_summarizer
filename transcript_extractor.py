from collections import OrderedDict
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import os, json, pytz, yt_dlp, webvtt, config



class YouTubeTranscriptExtractor:

    def __init__(self):
        """Initialize extractor with configuration"""
        self.config = config
        self.logger = self.config.LOGGER
        os.makedirs(self.config.VTT_FILES, exist_ok=True)

    def convert_timestamp(self,timestamp):
        """
        Convert WebVTT timestamp to seconds
        Handles formats like '00:00:07.349'
        """
        try:
            parts = timestamp.split(':')
            hours = float(parts[0])
            minutes = float(parts[1])
            seconds = float(parts[2])
            return hours * 3600 + minutes * 60 + seconds
        except Exception:
            return 0

    def process_input_json(self) -> Optional[List[Dict]]:
        """Process input JSON and extract transcripts"""
        # Check if input file exists
        if not os.path.exists(self.config.EXTRACTED_VIDEOS_FILE):
            self.logger.error(f"Input file not found: {self.config.EXTRACTED_VIDEOS_FILE}")
            return None
        
        # Read input JSON
        with open(self.config.EXTRACTED_VIDEOS_FILE, 'r') as f:
            input_data = json.load(f)
        
        # Output data structure
        output_data = []
        
        for channel_data in input_data:
            channel_name = channel_data.get('channel_name', '')
            channel_videos = []
            
            for video in channel_data.get('videos', []):
                # Extract title and upload time
                title = video.get('title', '')
                upload_time = video.get('upload_time', '')
                video_id = video.get('id', '')
                
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                try:
                    # Extract transcript using video ID
                    transcript_data = self._extract_transcript(video_url)
                    if transcript_data:
                        channel_videos.append({
                            'title': title,
                            'upload_time': upload_time,
                            "transcript_data":transcript_data
                        })
                except Exception as e:
                    self.logger.error(f"Error processing video {title}: {e}")
            
            # Add channel data to output if it matches input structure
            output_data.append({
                'channel_name': channel_name,
                'videos': channel_videos
            })
        
        with open(self.config.VIDEO_TRANSCRIPT_FILE ,'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)
        
        self.logger.info(f"Saved output to {self.config.VIDEO_TRANSCRIPT_FILE}")
        
        return output_data

    def _extract_transcript(self, video_url: str) -> Optional[Dict]:

        """Extract transcript for a given video URL"""
        video_id = video_url.split('=')[-1]
        
        ydl_opts = {
            'skip_download': True,
            'writeautomaticsub': True,
            'subtitleslangs': self.config.SUBTITLE_LANGS,
            'outtmpl':os.path.join(self.config.VTT_FILES, f'{video_id}.%(ext)s')
        }
        
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(video_url, download=False)
                ydl.download([video_url])
            except Exception as e:
                print(f"Download error: {e}")
                return
        
        vtt_file = os.path.join(self.config.VTT_FILES, f'{video_id}.en.vtt')
        
        if not os.path.exists(vtt_file):
            print("No subtitles found.")
            return
        
        try:
            # Read all captions with timestamps
            captions = webvtt.read(vtt_file)
            
            # Get chapters 
            chapters = info_dict.get('chapters', [])
            
            # Initialize chapter transcripts dictionary
            chapter_transcript = {}
            
            if chapters:
                # Process with chapters
                for i, chapter in enumerate(chapters):
                    start_time = chapter.get('start_time', 0)
                    # Get next chapter's start time or use video duration if last chapter
                    end_time = chapters[i+1].get('start_time', float('inf')) if i+1 < len(chapters) else float('inf')
                    
                    # Filter captions for this chapter
                    chapter_captions = [
                        caption.text.replace('\n', ' ').strip() 
                        for caption in captions 
                        if start_time <= self.convert_timestamp(caption.start) < end_time
                    ]
                   
                    # Remove duplicates while preserving order
                    unique_captions = list(OrderedDict.fromkeys(filter(bool, chapter_captions)))
                    
                    chapter_transcript[chapter['title']] = ' '.join(unique_captions)
            else:
                # If no chapters, use entire transcript
                full_captions = [
                    caption.text.replace('\n', ' ').strip() 
                    for caption in captions
                ]
                # Remove duplicates while preserving order
                unique_captions = list(OrderedDict.fromkeys(filter(bool, full_captions)))
                
                chapter_transcript['Full Video'] = ' '.join(unique_captions)
            return chapter_transcript

        except Exception as e:
            self.logger.error(f"Transcript extraction error for {video_url}: {e}")
            return None

def TranscriptExtractor():
    """Main entry point for the script"""
    extractor = YouTubeTranscriptExtractor()
    extractor.process_input_json()
