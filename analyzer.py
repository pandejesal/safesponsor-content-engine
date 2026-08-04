import json
from google import genai


def analyze_transcript(transcript: str, api_key: str) -> dict:
    """Analyze transcript using Gemini AI for brand safety and content generation."""
    client = genai.Client(api_key=api_key)
    
    prompt = f"""You are SafeSponsor AI, a creator brand safety and sponsorship vetting platform.

Analyze the following YouTube video transcript and provide a comprehensive sponsorship suitability assessment.

TONE REQUIREMENTS:
- Professional, data-driven, objective
- Like a vetting report for marketing executives evaluating creator partnerships
- NO hype words or clickbait language
- Focus on actionable metrics: Risk Score, Content Flags, Audience Safety, Sponsorship Readiness

1. SPONSORSHIP VETTING ASSESSMENT:
   - risk_score: Integer 0-100 (0 = fully safe for sponsorship, 100 = high risk)
   - risk_level: "LOW" (0-30), "MEDIUM" (31-60), or "HIGH" (61-100)
   - summary: 2-sentence professional assessment of sponsorship suitability
   - flagged_keywords: Array of potentially problematic terms found (max 5)
   - transcript_flags: Object with slurs_count, policy_flags_count, profanity_count
   - comment_sentiment: Estimated positive sentiment percentage (integer 0-100)
   - sponsorship_suitability: "RECOMMENDED", "CAUTION", or "NOT RECOMMENDED"
   - audience_alignment: Description of typical audience demographic fit

2. CONTENT REPLICATION (professional creator economy content):
   - linkedin_carousel: Array of 5 slide objects, each with:
     * slide: slide number (1-5)
     * title: Data-focused headline
     * body: Informative content (2-3 sentences)
   - twitter_thread: Array of 4 tweet strings (under 280 chars, industry tone)
   - instagram_caption: Professional caption with minimal emojis, B2B hashtags

3. VIDEO REEL SCRIPT (25-second sponsorship audit):
   - reel_script: Object with:
     * hook: Professional context statement (0-5s). Example: "Creator sponsorship vetting report for this channel."
     * body: Objective data analysis with specific metrics (5-20s)
     * cta: Clean CTA for brands/creators to run free audit at safe-sponsor-ai.vercel.app (20-25s)

TRANSCRIPT:
{transcript}

Return ONLY valid JSON in this exact format:
{{
  "risk_score": 12,
  "risk_level": "LOW",
  "summary": "This creator channel demonstrates strong brand safety metrics suitable for enterprise sponsorship. Transcript analysis reveals minimal risk factors across all evaluated categories.",
  "flagged_keywords": [],
  "transcript_flags": {{
    "slurs_count": 0,
    "policy_flags_count": 0,
    "profanity_count": 0
  }},
  "comment_sentiment": 88,
  "sponsorship_suitability": "RECOMMENDED",
  "audience_alignment": "General audience with family-friendly content preferences",
  "linkedin_carousel": [
    {{"slide": 1, "title": "...", "body": "..."}},
    {{"slide": 2, "title": "...", "body": "..."}},
    {{"slide": 3, "title": "...", "body": "..."}},
    {{"slide": 4, "title": "...", "body": "..."}},
    {{"slide": 5, "title": "...", "body": "..."}}
  ],
  "twitter_thread": ["...", "...", "...", "..."],
  "instagram_caption": "...",
  "reel_script": {{
    "hook": "Creator sponsorship vetting report for this channel.",
    "body": "Transcript analysis identified zero policy violations and zero profanity. The overall brand safety score is 12 out of 100, with 88 percent positive audience sentiment. This creator is recommended for standard sponsorship campaigns.",
    "cta": "Run a free creator safety audit at safe-sponsor-ai.vercel.app"
  }}
}}"""
    
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )
    
    result_text = response.text.strip()
    
    if result_text.startswith("```"):
        result_text = result_text.split("```")[1]
        if result_text.startswith("json"):
            result_text = result_text[4:]
    
    return json.loads(result_text)
