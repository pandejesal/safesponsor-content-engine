import json
from google import genai


def analyze_transcript(transcript: str, api_key: str) -> dict:
    """Analyze transcript using Gemini AI for brand safety and content generation."""
    client = genai.Client(api_key=api_key)
    
    prompt = f"""You are SafeSponsor AI, a professional brand safety intelligence platform for sponsorships.

Analyze the following YouTube video transcript and provide a comprehensive brand safety audit.

TONE REQUIREMENTS:
- Calm, articulate, professional, data-driven
- Like a product demo for marketing executives and professional creators
- NO hype words (no "insane", "mindblowing", "you won't believe", "stop scrolling")
- Focus on real metrics: Brand Safety Risk Score, Transcript Keyword Flags, Sponsorship Suitability

1. BRAND SAFETY ASSESSMENT:
   - risk_score: Integer 0-100 (0 = completely safe, 100 = extremely risky)
   - risk_level: "LOW" (0-30), "MEDIUM" (31-60), or "HIGH" (61-100)
   - summary: Professional 2-sentence explanation of the risk assessment
   - flagged_keywords: Array of problematic words/phrases found (max 5)
   - transcript_flags: Object with slurs_count, policy_flags_count, profanity_count
   - comment_sentiment: Estimated percentage of positive sentiment (integer 0-100)
   - sponsorship_suitability: "RECOMMENDED", "CAUTION", or "NOT RECOMMENDED"

2. CONTENT REPLICATION (based on the video's message):
   - linkedin_carousel: Array of 5 slide objects, each with:
     * slide: slide number (1-5)
     * title: slide headline (professional, data-focused)
     * body: slide content (2-3 sentences, informative)
   - twitter_thread: Array of 4 tweet strings (each under 280 chars, professional tone)
   - instagram_caption: Professional caption with minimal emojis, industry hashtags

3. VIDEO REEL SCRIPT (for a 25-second vertical video audit report):
   - reel_script: Object with:
     * hook: Calm, industry-relevant problem statement (0-5s). Example: "Brand safety risk assessment for this channel."
     * body: Objective analysis of transcript flags, sentiment, and risk score (5-20s). Include specific numbers.
     * cta: Clean call-to-action inviting brands or creators to run a free audit at safe-sponsor-ai.vercel.app (20-25s)

TRANSCRIPT:
{transcript}

Return ONLY valid JSON in this exact format (no markdown, no extra text):
{{
  "risk_score": 12,
  "risk_level": "LOW",
  "summary": "This channel demonstrates strong brand safety metrics. Transcript analysis reveals minimal risk factors suitable for most sponsorship categories.",
  "flagged_keywords": [],
  "transcript_flags": {{
    "slurs_count": 0,
    "policy_flags_count": 0,
    "profanity_count": 0
  }},
  "comment_sentiment": 88,
  "sponsorship_suitability": "RECOMMENDED",
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
    "hook": "Brand safety risk assessment for this channel.",
    "body": "Transcript analysis identified zero policy violations and zero profanity flags. The overall risk score is 12 out of 100, with an estimated 88 percent positive comment sentiment. Sponsorship suitability is recommended.",
    "cta": "Run a free brand safety audit at safe-sponsor-ai.vercel.app"
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
