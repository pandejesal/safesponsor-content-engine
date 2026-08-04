import json
import os
import sys
import io
from dotenv import load_dotenv
from fetcher import get_transcript_from_url
from analyzer import analyze_transcript
from generator import generate_carousel_assets
from reel_generator import generate_safesponsor_reel
from notifier import send_to_telegram

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
    print("\n[Step 1/5] Fetching YouTube transcript...")
    print(f"  URL: {url}")
    transcript_data = get_transcript_from_url(url)
    print(f"  Video ID: {transcript_data['video_id']}")
    print(f"  Transcript length: {len(transcript_data['transcript'])} characters")
    
    # Step 2: Analyze with Gemini AI
    print("\n[Step 2/5] Analyzing transcript with SafeSponsor AI...")
    analysis_result = analyze_transcript(transcript_data['transcript'], api_key)
    
    # Save analysis result
    with open("analysis_result.json", "w", encoding="utf-8") as f:
        json.dump(analysis_result, f, indent=2, ensure_ascii=False)
    print("  Analysis saved to analysis_result.json")
    
    # Step 3: Generate Visual Assets
    print("\n[Step 3/5] Generating LinkedIn carousel assets...")
    asset_paths = generate_carousel_assets(analysis_result)
    
    # Step 4: Generate SafeSponsor Reel
    print("\n[Step 4/5] Generating brand safety audit reel...")
    reel_script = analysis_result.get("reel_script", {})
    reel_paths = generate_safesponsor_reel(reel_script, analysis_result)
    
    # Step 5: Send to Telegram
    print("\n[Step 5/5] Sending to Telegram...")
    telegram_success = send_to_telegram(
        asset_paths['pdf'],
        analysis_result['twitter_thread'],
        analysis_result['instagram_caption'],
        reel_paths['reel']
    )
    
    if telegram_success:
        print("\nContent successfully dispatched to Telegram!")
    
    # Print Social Media Content
    print("\n" + "=" * 60)
    print("RISK ASSESSMENT")
    print("=" * 60)
    print(f"  Risk Score: {analysis_result['risk_score']}/100")
    print(f"  Risk Level: {analysis_result['risk_level']}")
    print(f"  Sponsorship Suitability: {analysis_result.get('sponsorship_suitability', 'N/A')}")
    print(f"  Summary: {analysis_result['summary']}")
    
    if analysis_result.get('flagged_keywords'):
        print(f"  Flagged Keywords: {', '.join(analysis_result['flagged_keywords'])}")
    
    transcript_flags = analysis_result.get('transcript_flags', {})
    if transcript_flags:
        print(f"  Transcript Flags: {transcript_flags.get('slurs_count', 0)} slurs, {transcript_flags.get('policy_flags_count', 0)} policy flags, {transcript_flags.get('profanity_count', 0)} profanity")
    
    print(f"  Comment Sentiment: {analysis_result.get('comment_sentiment', 'N/A')}%")
    
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
    print(f"  Audit Reel: {reel_paths['reel']}")
    
    print("\n" + "=" * 60)
    print("Pipeline complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
