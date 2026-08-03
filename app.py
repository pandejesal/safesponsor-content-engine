import json
import os
import sys
import io
from dotenv import load_dotenv
from fetcher import get_transcript_from_url
from analyzer import analyze_transcript
from generator import generate_carousel_assets

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def main():
    if len(sys.argv) < 2:
        print("Usage: python app.py <youtube_url>")
        print("Example: python app.py https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        sys.exit(1)
    
    url = sys.argv[1]
    
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file")
        sys.exit(1)
    
    print("=" * 60)
    print("SafeSponsor AI - Content Engine Pipeline")
    print("=" * 60)
    
    # Step 1: Fetch Transcript
    print("\n[Step 1/4] Fetching YouTube transcript...")
    print(f"  URL: {url}")
    transcript_data = get_transcript_from_url(url)
    print(f"  Video ID: {transcript_data['video_id']}")
    print(f"  Transcript length: {len(transcript_data['transcript'])} characters")
    
    # Step 2: Analyze with Gemini AI
    print("\n[Step 2/4] Analyzing transcript with SafeSponsor AI...")
    analysis_result = analyze_transcript(transcript_data['transcript'], api_key)
    
    # Save analysis result
    with open("analysis_result.json", "w", encoding="utf-8") as f:
        json.dump(analysis_result, f, indent=2, ensure_ascii=False)
    print("  Analysis saved to analysis_result.json")
    
    # Step 3: Generate Visual Assets
    print("\n[Step 3/4] Generating LinkedIn carousel assets...")
    asset_paths = generate_carousel_assets(analysis_result)
    
    # Step 4: Print Social Media Content
    print("\n[Step 4/4] Social Media Content Ready!")
    print("\n" + "=" * 60)
    print("RISK ASSESSMENT")
    print("=" * 60)
    print(f"  Risk Score: {analysis_result['risk_score']}/100")
    print(f"  Risk Level: {analysis_result['risk_level']}")
    print(f"  Summary: {analysis_result['summary']}")
    
    if analysis_result.get('flagged_keywords'):
        print(f"  Flagged Keywords: {', '.join(analysis_result['flagged_keywords'])}")
    
    print("\n" + "=" * 60)
    print("TWITTER THREAD")
    print("=" * 60)
    for i, tweet in enumerate(analysis_result['twitter_thread'], 1):
        print(f"\n  Tweet {i}:")
        print(f"  {tweet}")
    
    print("\n" + "=" * 60)
    print("INSTAGRAM CAPTION")
    print("=" * 60)
    print(f"\n  {analysis_result['instagram_caption']}")
    
    print("\n" + "=" * 60)
    print("GENERATED ASSETS")
    print("=" * 60)
    print(f"  Slides: {len(asset_paths['slides'])} PNG files")
    for slide_path in asset_paths['slides']:
        print(f"    - {slide_path}")
    print(f"  PDF: {asset_paths['pdf']}")
    
    print("\n" + "=" * 60)
    print("Pipeline complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
