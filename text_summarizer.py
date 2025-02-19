from typing import List, Dict, Optional
import os, json, config, requests
from tqdm import tqdm
import os,tiktoken,re
import time

class TranscriptSummarizer:

    def __init__(self):
        """
        Initialize summarizer with configuration
        
        Args:
            ollama_url (str): URL for Ollama API
        """
        self.config = config
        self.ollama_url = self.config.OLLAMA_URL
        self.logger = self.config.LOGGER 
        self.model=self.config.OLLAMA_MODEL


   
    

    def summarize_chunk(self, text):
        """
        Summarizes input text using Groq API with specific formatting requirements.
        
        Args:
            text (str): The text content to be summarized
            
        Returns:
            str: The summarized text response
        """
        # Set your Groq API key
        try:
            
            payload = {
                "model": self.model,
                "prompt":  f"""Summarize the following YouTube video transcript concisely in  points. 
                Specific requirements:\n
                    --IMPORTANT:
                - Maximum 3 lines\n
                - Be very short and concise\n
                - Do not miss any important details\n
                - Focus only on the key information of what the video discusses\n
                - Exclude any personal details about the narrator\n"
                - Remove repeated phrases and unnecessary details\n
                - Use precise, information-dense language\n\n
                Content: {text}""",
                "stream": False,
            }
            
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            
            return response.json().get('response', '')
        
        except Exception as e:
            self.logger.error(f"Summarization error: {e}")
            return ""

    def summarize_video_description(self, transcripts: List[str]) -> str:
        """
        Generate overall video description with context accumulation
        
        Args:
            transcripts (List[str]): Transcript chunks
        
        Returns:
            str: Comprehensive video description
        """
        running_summary = ""
        
        for i, transcript in enumerate(tqdm(transcripts)):
            try:
                payload = {
                    "model": self.model,
                    "prompt":f"""You are summarizing a YouTube video by analyzing it in chunks. 
                                Summarization Guidelines:
                                    --IMPORTANT:
                                        - Create a maximum of 5  lines .
                                - Be extremely concise yet comprehensive
                                - Capture the video's core essence
                                - Ensure no critical information is missed
                                - Focus on main purpose and key topics
                                - Prioritize factual, content-driven summary
                                - Eliminate repetitive or unnecessary details

                                Objective: Craft a summary that provides a understanding of the video's content in just a glance.

                                ###Previously generated combined summary of the chunks summarized so far:

                                {running_summary}

                                ### New Transcript Chunk:
                                {transcript}

                                Output Format: Numbered points(very short in length), information-dense, zero fluff.""",
                    "stream": False
                }
                
                response = requests.post(self.ollama_url, json=payload)
                response.raise_for_status()
                
                running_summary = response.json().get('response', '')
            
            except Exception as e:
                self.logger.error(f"Description generation error at chunk {i}: {e}")
        
        return running_summary

    def process_channels(self) -> Optional[List[Dict]]:
        """
        Process YouTube channel transcripts
        
        Args:
            input_file (str): Input JSON file path
            output_file (str): Output JSON file path
        
        Returns:
            Optional[List[Dict]]: Processed channel data
        """
        # Validate input file
        if not os.path.exists(self.config.VIDEO_TRANSCRIPT_FILE):
            self.logger.error(f"Input file not found: {self.config.VIDEO_TRANSCRIPT_FILE}")
            return None

        with open(self.config.VIDEO_TRANSCRIPT_FILE, 'r', encoding='utf-8') as f:
            channels_data = json.load(f)
        
        for channel in channels_data:
            if channel['videos']:
                for video in channel['videos']:
                    if 'transcript_data' in video:
                        # Chapter-level summarization
                        chapter_summaries = {}
                        video_summary_chunks = []
                        
                        for chapter, content in tqdm(video['transcript_data'].items()):
                            # Split long chapters into chunks
                            chunks = self.split_text_into_chunks(content)
                            
                            # Summarize chapter chunks independently
                            chapter_summary = []
                            for chunk in chunks:
                                
                                chunk_summary = self.summarize_chunk(chunk)
                                time.sleep(20)
                                chapter_summary.append(chunk_summary)
                                video_summary_chunks.append(chunk)
                               

                            
                            # Combine chapter summaries
                            final_chapter_summary = " ".join(chapter_summary)
                            chapter_summaries[chapter] = final_chapter_summary
                            
                        
                        # Store chapter summaries
                        video['chapter_summaries'] = chapter_summaries
                        
                        # Generate overall video description
                        video['description'] = self.summarize_video_description(video_summary_chunks)
                        
                        # Remove original transcript data
                        del video['transcript_data']
        
        # Write processed data
        with open(self.config.SUMMARIZED_TRANSCRIPT_FILE, 'w', encoding='utf-8') as f:
            json.dump(channels_data, f, indent=4, ensure_ascii=False)
        
        self.logger.info(f"Processed data saved to {self.config.SUMMARIZED_TRANSCRIPT_FILE}")
        return channels_data

    def split_text_into_chunks(self,text: str) -> List[str]:
        """
        Split text into chunks based on token count
        
        Args:
            text (str): Input text
            max_tokens (int): Maximum tokens per chunk (default 30000)
        
        Returns:
            List[str]: List of text chunks, each containing max_tokens or fewer tokens
        """
        max_tokens=30000
        # Initialize tokenizer (using cl100k_base which is compatible with most modern models)
        tokenizer = tiktoken.get_encoding("cl100k_base")
        text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', str(text))  # Remove control characters

        # Get all tokens for the text
        tokens = tokenizer.encode(text)
        
        # Initialize variables for chunking
        chunks = []
        current_chunk_tokens = []
        current_token_count = 0
        
        # Process tokens
        for token in tokens:
            if current_token_count >= max_tokens:
                # Convert tokens back to text and add to chunks
                chunk_text = tokenizer.decode(current_chunk_tokens)
                chunks.append(chunk_text)
                # Reset current chunk
                current_chunk_tokens = []
                current_token_count = 0
            
            current_chunk_tokens.append(token)
            current_token_count += 1
        
        # Add the last chunk if it exists
        if current_chunk_tokens:
            chunk_text = tokenizer.decode(current_chunk_tokens)
            chunks.append(chunk_text)
        
        return chunks


def TranscriptSummarizerProcess():
    
    summarizer = TranscriptSummarizer()
    summarizer.process_channels()

