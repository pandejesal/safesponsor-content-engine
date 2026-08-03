import json
from google import genai


def analyze_transcript(transcript: str, api_key: str) -> dict:
    """Analyze transcript using Gemini AI for brand safety and content generation."""
    client = genai.Client(api_key=api_key)
    
    prompt = f"""You are SafeSponsor AI, a brand safety analysis tool for sponsorships.

Analyze the following YouTube video transcript and provide:

1. BRAND SAFETY ASSESSMENT:
   - risk_score: Integer 0-100 (0 = completely safe, 100 = extremely risky)
   - risk_level: "LOW" (0-30), "MEDIUM" (31-60), or "HIGH" (61-100)
   - summary: Brief explanation of the risk assessment
   - flagged_keywords: Array of potentially problematic words/phrases found

2. CONTENT REPLICATION (based on the video's message):
   - linkedin_carousel: Array of 5 slide objects, each with:
     * slide: slide number (1-5)
     * title: slide headline
     * body: slide content (2-3 sentences)
   - twitter_thread: Array of 4 tweet strings (each under 280 chars)
   - instagram_caption: Engaging caption with emojis and hashtags

3. VIDEO REEL SCRIPT (for a 30-second vertical video):
   - reel_script: Object with:
     * hook: Attention-grabbing opening line (5-7 seconds)
     * body: Main message explaining the analysis (15-20 seconds)
     * cta: Call to action directing to safe-sponsor-ai.vercel.app (5-7 seconds)

TRANSCRIPT:
{transcript}

Return ONLY valid JSON in this exact format (no markdown, no extra text):
{{
  "risk_score": 0,
  "risk_level": "LOW",
  "summary": "...",
  "flagged_keywords": [],
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
    "hook": "Stop sponsoring YouTube creators before running this 10-second check.",
    "body": "We ran SafeSponsor AI on a recent viral video. The risk score was 18 out of 100, but our transcript analysis flagged 2 hidden copyright keywords.",
    "cta": "Check your channel brand safety score at safe-sponsor-ai.vercel.app"
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
