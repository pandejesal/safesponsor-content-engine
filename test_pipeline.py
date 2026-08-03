import json
import os
import sys
from dotenv import load_dotenv
from fetcher import get_transcript_from_url
from analyzer import analyze_transcript


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_pipeline.py <youtube_url>")
        print("Example: python test_pipeline.py https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        sys.exit(1)
    
    url = sys.argv[1]
    
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file")
        sys.exit(1)
    
    print(f"Fetching transcript from: {url}")
    transcript_data = get_transcript_from_url(url)
    print(f"Video ID: {transcript_data['video_id']}")
    print(f"Transcript length: {len(transcript_data['transcript'])} characters")
    
    print("\nAnalyzing transcript with SafeSponsor AI...")
    analysis_result = analyze_transcript(transcript_data['transcript'], api_key)
    
    output_file = "analysis_result.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(analysis_result, f, indent=2, ensure_ascii=False)
    
    print(f"\nAnalysis complete! Results saved to: {output_file}")
    print(f"\nRisk Assessment:")
    print(f"  Score: {analysis_result['risk_score']}/100")
    print(f"  Level: {analysis_result['risk_level']}")
    print(f"  Summary: {analysis_result['summary']}")
    
    return analysis_result


if __name__ == "__main__":
    main()
