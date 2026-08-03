import re
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from any YouTube URL format."""
    patterns = [
        r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:embed/)([a-zA-Z0-9_-]{11})',
        r'(?:shorts/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    raise ValueError(f"Could not extract video ID from URL: {url}")


def fetch_transcript(video_id: str) -> str:
    """Fetch transcript for a YouTube video and return as full text."""
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id, languages=['en'])
    
    full_text = ' '.join([snippet.text for snippet in transcript.snippets])
    
    return full_text


def get_transcript_from_url(url: str) -> dict:
    """Main function: extract video ID and fetch transcript from URL."""
    video_id = extract_video_id(url)
    transcript_text = fetch_transcript(video_id)
    
    return {
        "video_id": video_id,
        "transcript": transcript_text
    }
