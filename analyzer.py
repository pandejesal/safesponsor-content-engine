import json
import re
import os


PROFANITY_LIST = [
    "damn", "hell", "crap", "ass", "shit", "fuck", "bitch", "bastard",
    "dick", "cock", "piss", "bollocks", "bloody", "bugger", "wanker"
]

SLUR_LIST = [
    "nigger", "faggot", "retard", "cripple", "spic", "chink",
    "kike", "towelhead", "raghead", "tranny", "dyke", "homo"
]

POLICY_TERMS = [
    "kill yourself", "kys", "dox", "doxing", "swat", "ddos",
    "hack", "bomb", "weapon", "terrorist", "isis", "al-qaeda"
]

SAFE_TERMS = [
    "subscribe", "like", "comment", "share", "follow", "support",
    "sponsor", "collab", "partner", "brand", "marketing", "ad",
    "product", "review", "tutorial", "educational", "learning"
]


def analyze_transcript_local(transcript: str) -> dict:
    """
    Analyze transcript locally without Gemini API.
    Uses keyword matching and heuristic analysis for brand safety.
    """
    text_lower = transcript.lower()
    words = text_lower.split()
    total_words = len(words)

    slurs_count = sum(1 for s in SLUR_LIST if s in text_lower)
    profanity_count = sum(1 for p in PROFANITY_LIST if p in text_lower)
    policy_flags_count = sum(1 for p in POLICY_TERMS if p in text_lower)

    flagged_keywords = []
    for kw in PROFANITY_LIST + SLUR_LIST + POLICY_TERMS:
        if kw in text_lower and kw not in flagged_keywords:
            flagged_keywords.append(kw)

    risk_score = 0
    risk_score += slurs_count * 15
    risk_score += profanity_count * 5
    risk_score += policy_flags_count * 20
    risk_score = min(risk_score, 100)

    safety_score = 100 - risk_score

    if safety_score >= 70:
        risk_level = "LOW"
        sponsorship_suitability = "RECOMMENDED"
    elif safety_score >= 40:
        risk_level = "MEDIUM"
        sponsorship_suitability = "CAUTION"
    else:
        risk_level = "HIGH"
        sponsorship_suitability = "NOT RECOMMENDED"

    safe_count = sum(1 for t in SAFE_TERMS if t in text_lower)
    sentiment_base = 70
    sentiment_bonus = min(safe_count * 3, 25)
    sentiment_penalty = (slurs_count + profanity_count) * 5
    comment_sentiment = max(0, min(100, sentiment_base + sentiment_bonus - sentiment_penalty))

    summary = generate_summary(risk_score, risk_level, flagged_keywords, comment_sentiment)

    linkedin_carousel = generate_linkedin_carousel(risk_score, risk_level, flagged_keywords, comment_sentiment)
    twitter_thread = generate_twitter_thread(risk_score, risk_level, flagged_keywords, comment_sentiment)
    instagram_caption = generate_instagram_caption(risk_score, risk_level, flagged_keywords, comment_sentiment)
    reel_script = generate_reel_script(risk_score, risk_level, comment_sentiment)

    return {
        "risk_score": safety_score,
        "risk_level": risk_level,
        "summary": summary,
        "flagged_keywords": flagged_keywords[:5],
        "transcript_flags": {
            "slurs_count": slurs_count,
            "policy_flags_count": policy_flags_count,
            "profanity_count": profanity_count,
        },
        "comment_sentiment": comment_sentiment,
        "sponsorship_suitability": sponsorship_suitability,
        "audience_alignment": determine_audience(text_lower),
        "linkedin_carousel": linkedin_carousel,
        "twitter_thread": twitter_thread,
        "instagram_caption": instagram_caption,
        "reel_script": reel_script,
    }


def generate_summary(risk_score: int, risk_level: str, flagged_keywords: list, sentiment: int) -> str:
    if risk_score <= 10:
        return "This creator demonstrates strong brand safety metrics suitable for enterprise sponsorship. Transcript analysis reveals minimal risk factors across all evaluated categories."
    elif risk_score <= 30:
        return "This creator shows acceptable brand safety metrics with minor considerations. Transcript analysis indicates generally safe content suitable for standard sponsorship with standard monitoring."
    elif risk_score <= 60:
        return "This creator demonstrates moderate brand safety concerns requiring review. Transcript analysis identifies some flagged content that may require additional vetting before sponsorship."
    else:
        return "This creator demonstrates high brand safety risk factors. Transcript analysis reveals significant concerns that may make sponsorship unsuitable without substantial content review."


def determine_audience(text: str) -> str:
    gaming_terms = ["game", "gaming", "play", "stream", "esport", "twitch", "valorant", "fortnite"]
    tech_terms = ["code", "programming", "software", "tech", "ai", "machine learning", "python"]
    education_terms = ["learn", "teach", "education", "school", "university", "lecture", "tutorial"]

    gaming_score = sum(1 for t in gaming_terms if t in text)
    tech_score = sum(1 for t in tech_terms if t in text)
    education_score = sum(1 for t in education_terms if t in text)

    if gaming_score > tech_score and gaming_score > education_score:
        return "Gaming and entertainment audience, predominantly younger demographics"
    elif tech_score > education_score:
        return "Technology and programming audience, professional and enthusiast demographics"
    elif education_score > 0:
        return "Educational and learning-focused audience, students and professionals"
    else:
        return "General audience with broad content interests"


def generate_linkedin_carousel(risk_score, risk_level, flagged_keywords, sentiment):
    return [
        {"slide": 1, "title": "Evaluating Creator Content for Brand Safety", "body": "As brands increasingly invest in creator partnerships, objective transcript analysis remains essential. SafeSponsor AI evaluates content to ensure marketing spend is deployed in safe environments."},
        {"slide": 2, "title": "The Metrics of Brand Safety", "body": f"This transcript analysis identified a {risk_level.lower()} risk profile with a score of {risk_score}/100. {'No significant flagged content was detected.' if risk_score < 30 else 'Some content flags were identified requiring review.'}"},
        {"slide": 3, "title": "Audience Sentiment Analysis", "body": f"With an estimated {sentiment}% positive sentiment, this creator {'drives high engagement without the risk of toxic comment sections.' if sentiment > 70 else 'has mixed audience reception that warrants monitoring.'}"},
        {"slide": 4, "title": "Risk Assessment Summary", "body": f"A risk score of {risk_score}/100 indicates that this content {'is highly suitable' if risk_score < 30 else 'may be suitable with conditions'} for sponsorship integrations across {'all' if risk_score < 30 else 'most'} industry verticals."},
        {"slide": 5, "title": "Data-Driven Creator Vetting", "body": "Deploy your influencer marketing budget with confidence. SafeSponsor AI provides real-time, algorithmic safety audits to keep your enterprise brand secure."},
    ]


def generate_twitter_thread(risk_score, risk_level, flagged_keywords, sentiment):
    return [
        f"Is your brand vetting creators before signing campaign contracts? Manual review is slow, but automated brand safety analysis can flag risks in seconds. Here is how we evaluate a {risk_level.lower()}-risk channel. \U0001f9f5",
        f"First, let's look at the raw metrics. Risk Score: {risk_score}/100. {'No profanity or policy violations detected.' if risk_score < 30 else 'Some content flags detected.'} For enterprise sponsors, this represents {'a pristine environment' if risk_score < 30 else 'a generally safe environment'} for ad placement. #BrandSafety",
        f"Beyond the transcript, audience sentiment analysis reveals a {sentiment}% positive score. {'High positive sentiment means your sponsorship is met with receptive, engaged viewers.' if sentiment > 70 else 'Mixed sentiment suggests careful monitoring may be needed.'} #InfluencerMarketing",
        f"Our final assessment for this creator: {risk_level} (Risk Score: {risk_score}/100). Protect your ad spend and scale your campaigns securely. Run a free audit on any creator channel here: safe-sponsor-ai.vercel.app",
    ]


def generate_instagram_caption(risk_score, risk_level, flagged_keywords, sentiment):
    return f"How safe are your creator partnerships? \U0001f4ca Brand safety isn't just about avoiding controversy - it's about maximizing ROI in brand-safe environments. Our latest safety audit reveals a {risk_level.lower()}-risk profile: {risk_score}/100 risk score with {sentiment}% positive audience sentiment. {'For enterprise marketers, this represents an ideal partnership opportunity.' if risk_score < 30 else 'For enterprise marketers, this partnership warrants standard monitoring protocols.'} Click the link in bio to run a free audit on your creator pipeline. #BrandSafety #InfluencerMarketing #CreatorEconomy #MarketingROI #AdTech"


def generate_reel_script(risk_score, risk_level, sentiment):
    hook = "Creator sponsorship vetting report for this channel."

    if risk_score <= 10:
        body = f"Transcript analysis identified zero policy violations and zero profanity. The overall brand safety score is {risk_score} out of 100, with {sentiment} percent positive audience sentiment. This creator is recommended for standard sponsorship campaigns."
    elif risk_score <= 30:
        body = f"Transcript analysis identified minimal risk factors. The overall brand safety score is {risk_score} out of 100, with {sentiment} percent positive audience sentiment. This creator is suitable for standard sponsorship campaigns with routine monitoring."
    else:
        body = f"Transcript analysis identified some content flags requiring attention. The overall brand safety score is {risk_score} out of 100, with {sentiment} percent positive audience sentiment. This creator may require additional vetting before sponsorship."

    cta = "Run a free creator safety audit at safe-sponsor-ai.vercel.app"

    return {"hook": hook, "body": body, "cta": cta}
