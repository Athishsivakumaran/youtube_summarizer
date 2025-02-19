from tqdm import tqdm
import os, shutil, config
from text_summarizer import TranscriptSummarizerProcess
from videos_extractor import VideoExtractor 
from messages_sender import MessageSenderProcess
from transcript_extractor import TranscriptExtractor 


def setup_output_directory():
    if os.path.exists(config.OUTPUT_DIR):
        shutil.rmtree(config.OUTPUT_DIR)
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)


def main():
    steps = [
        ("Setting up output directory",setup_output_directory),
        ("Extracting videos", VideoExtractor),
        ("Extracting transcripts", TranscriptExtractor),
        ("Summarizing transcripts", TranscriptSummarizerProcess),
        ("Sending messages", MessageSenderProcess)
    ]
    
    with tqdm(total=len(steps), desc="Overall Progress", unit="step") as progress_bar:
        for step_description, step_function in steps:
            tqdm.write(f"Starting: {step_description}")
            step_function()
            progress_bar.update(1)

if __name__ == "__main__":
    main()
