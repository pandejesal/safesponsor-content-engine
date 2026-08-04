import os
import math
import wave
import struct
from pathlib import Path
from playwright.sync_api import sync_playwright
from moviepy import ImageClip, concatenate_videoclips


def get_gauge_color(score):
    if score <= 30:
        return "#22c55e"
    elif score <= 60:
        return "#eab308"
    return "#ef4444"


def get_gauge_degrees(score):
    return int((score / 100) * 360)


def get_risk_status(score):
    if score <= 30:
        return "LOW RISK"
    elif score <= 60:
        return "MODERATE"
    return "HIGH RISK"


def get_status_class(score):
    if score <= 30:
        return "status-low"
    elif score <= 60:
        return "status-medium"
    return "status-high"


def generate_keyword_pills(keywords):
    if not keywords:
        return '<span class="keyword-pill">No flags</span>'
    return "".join(f'<span class="keyword-pill">{kw}</span>' for kw in keywords[:5])


def generate_tone(frequency=440, duration_ms=100, volume=0.3, fade_ms=20):
    sample_rate = 22050
    num_samples = int(sample_rate * duration_ms / 1000)
    fade_samples = int(sample_rate * fade_ms / 1000)
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        val = volume * math.sin(2 * math.pi * frequency * t)
        if i < fade_samples:
            val *= i / fade_samples
        elif i > num_samples - fade_samples:
            val *= (num_samples - i) / fade_samples
        samples.append(int(val * 32767))
    return samples


def create_sfx_wav(path):
    samples = generate_tone(800, 40, 0.2, 10)
    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(22050)
        f.writeframes(struct.pack(f"<{len(samples)}h", *samples))


def build_full_html(
    risk_score, risk_status, status_class, summary,
    gauge_color, gauge_degrees, video_title,
    slurs_count, policy_flags, profanity_count,
    comment_sentiment, keywords_html, cta_text
):
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;width:1080px;height:1920px;background:#09090b;overflow:hidden;}}
.audit-card{{background:#18181b;border:1px solid #27272a;border-radius:16px;}}
.metric-card{{background:#09090b;border:1px solid #27272a;border-radius:12px;}}
.gauge-ring{{width:200px;height:200px;border-radius:50%;background:conic-gradient(from 180deg,{gauge_color} 0deg,{gauge_color} {gauge_degrees}deg,#27272a {gauge_degrees}deg,#27272a 360deg);display:flex;align-items:center;justify-content:center;}}
.gauge-inner{{width:160px;height:160px;border-radius:50%;background:#18181b;display:flex;flex-direction:column;align-items:center;justify-content:center;}}
.gauge-value{{font-size:48px;font-weight:600;color:#fafafa;line-height:1;}}
.gauge-label{{font-size:12px;font-weight:500;color:#71717a;text-transform:uppercase;letter-spacing:1px;margin-top:4px;}}
.status-badge{{display:inline-flex;align-items:center;gap:6px;padding:6px 12px;border-radius:6px;font-size:12px;font-weight:500;text-transform:uppercase;letter-spacing:0.5px;}}
.status-low{{background:rgba(34,197,94,0.1);color:#22c55e;border:1px solid rgba(34,197,94,0.2);}}
.status-medium{{background:rgba(234,179,8,0.1);color:#eab308;border:1px solid rgba(234,179,8,0.2);}}
.status-high{{background:rgba(239,68,68,0.1);color:#ef4444;border:1px solid rgba(239,68,68,0.2);}}
.status-dot{{width:6px;height:6px;border-radius:50%;background:currentColor;}}
.sentiment-bar{{height:4px;background:#27272a;border-radius:2px;overflow:hidden;}}
.sentiment-fill{{height:100%;background:#22c55e;border-radius:2px;width:{comment_sentiment}%;}}
.keyword-pill{{display:inline-flex;align-items:center;padding:3px 10px;border-radius:9999px;font-size:12px;font-weight:500;background:#27272a;color:#d4d4d8;border:1px solid #3f3f46;}}
.anim{{opacity:0;transform:translateY(20px);transition:opacity 0.5s ease-out, transform 0.5s ease-out;}}
.anim.visible{{opacity:1;transform:translateY(0);}}
@keyframes pulse{{0%,100%{{opacity:1;}}50%{{opacity:0.5;}}}}
</style></head><body>
<div style="display:flex;flex-direction:column;height:100%;padding:48px;">
<header id="sec-header" class="anim" style="display:flex;align-items:center;justify-content:space-between;margin-bottom:40px;">
<div style="display:flex;align-items:center;gap:12px;">
<div style="width:32px;height:32px;background:#22c55e;border-radius:8px;display:flex;align-items:center;justify-content:center;">
<svg style="width:20px;height:20px;color:white;" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path></svg></div>
<span style="font-size:18px;font-weight:600;color:#fafafa;">SafeSponsor AI</span></div>
<span style="font-size:12px;font-weight:500;color:#71717a;text-transform:uppercase;letter-spacing:2px;">Sponsorship Vetting</span></header>
<div id="sec-card" class="anim" style="padding:32px;margin-bottom:24px;">
<div style="margin-bottom:24px;padding-bottom:24px;border-bottom:1px solid #27272a;">
<span style="font-size:12px;font-weight:500;color:#71717a;text-transform:uppercase;letter-spacing:1px;display:block;margin-bottom:8px;">Analyzing</span>
<h2 style="font-size:20px;font-weight:500;color:#fafafa;line-height:1.4;">{video_title}</h2></div>
<div style="display:flex;align-items:center;gap:32px;margin-bottom:24px;">
<div id="sec-score" class="anim" style="flex-shrink:0;">
<div class="gauge-ring">
<div class="gauge-inner"><span class="gauge-value">{risk_score}</span><span class="gauge-label">Risk Score</span></div></div></div>
<div style="flex:1;">
<div style="margin-bottom:16px;"><span class="status-badge {status_class}"><span class="status-dot"></span>{risk_status}</span></div>
<p style="font-size:14px;color:#a1a1aa;line-height:1.6;">{summary[:150]}</p></div></div>
<div id="sec-flags" class="anim" style="margin-bottom:24px;">
<span style="font-size:12px;font-weight:500;color:#71717a;text-transform:uppercase;letter-spacing:1px;display:block;margin-bottom:12px;">Transcript Analysis</span>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;">
<div class="metric-card" style="padding:16px;"><span style="font-size:24px;font-weight:600;color:#fafafa;display:block;">{slurs_count}</span><span style="font-size:12px;color:#71717a;">Slurs</span></div>
<div class="metric-card" style="padding:16px;"><span style="font-size:24px;font-weight:600;color:#fafafa;display:block;">{policy_flags}</span><span style="font-size:12px;color:#71717a;">Policy Flags</span></div>
<div class="metric-card" style="padding:16px;"><span style="font-size:24px;font-weight:600;color:#fafafa;display:block;">{profanity_count}</span><span style="font-size:12px;color:#71717a;">Profanity</span></div></div></div>
<div id="sec-sentiment" class="anim" style="margin-bottom:24px;">
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
<span style="font-size:12px;font-weight:500;color:#71717a;text-transform:uppercase;letter-spacing:1px;">Comment Sentiment</span>
<span style="font-size:14px;font-weight:600;color:#fafafa;">{comment_sentiment}%</span></div>
<div class="sentiment-bar"><div class="sentiment-fill"></div></div></div>
<div id="sec-keywords" class="anim">
<span style="font-size:12px;font-weight:500;color:#71717a;text-transform:uppercase;letter-spacing:1px;display:block;margin-bottom:12px;">Flagged Keywords</span>
<div style="display:flex;flex-wrap:wrap;gap:8px;">{keywords_html}</div></div></div>
<div style="flex:1;"></div>
<div id="sec-cta" class="anim" style="text-align:center;margin-bottom:32px;">
<p style="font-size:18px;font-weight:500;color:#d4d4d8;margin-bottom:16px;">{cta_text}</p>
<div style="display:inline-flex;align-items:center;gap:8px;padding:12px 24px;background:#16a34a;border-radius:8px;">
<span style="font-size:14px;font-weight:600;color:white;">safe-sponsor-ai.vercel.app</span></div></div>
<footer id="sec-footer" class="anim" style="display:flex;align-items:center;justify-content:space-between;padding-top:24px;border-top:1px solid rgba(39,39,42,0.5);">
<span style="font-size:12px;color:#52525b;">safe-sponsor-ai.vercel.app</span>
<div style="display:flex;align-items:center;gap:8px;">
<div style="width:6px;height:6px;background:#22c55e;border-radius:50%;animation:pulse 1.5s ease-in-out infinite;"></div>
<span style="font-size:12px;color:#71717a;font-weight:500;">LIVE AUDIT</span></div></footer>
</div></body></html>"""


def generate_safesponsor_reel(reel_script_data, analysis_data):
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    risk_score = analysis_data.get("risk_score", 0)
    flagged_keywords = analysis_data.get("flagged_keywords", [])
    summary = analysis_data.get("summary", "Analysis complete.")
    comment_sentiment = analysis_data.get("comment_sentiment", 88)
    audience_alignment = analysis_data.get("audience_alignment", "Creator Analysis")

    transcript_flags = analysis_data.get("transcript_flags", {})
    slurs_count = transcript_flags.get("slurs_count", 0)
    policy_flags = transcript_flags.get("policy_flags_count", 0)
    profanity_count = transcript_flags.get("profanity_count", 0)

    video_title = audience_alignment[:100] if audience_alignment else "Creator Analysis"
    gauge_color = get_gauge_color(risk_score)
    gauge_degrees = get_gauge_degrees(risk_score)
    risk_status = get_risk_status(risk_score)
    status_class = get_status_class(risk_score)
    keywords_html = generate_keyword_pills(flagged_keywords)
    cta_text = "Run a free creator safety audit"

    fps = 15
    total_duration = 8.0
    total_frames = int(total_duration * fps)

    print(f"  Rendering {total_frames} frames at {fps}fps with Playwright...")

    frames_dir = output_dir / "safesponsor_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    html_content = build_full_html(
        risk_score=risk_score, risk_status=risk_status,
        status_class=status_class, summary=summary,
        gauge_color=gauge_color, gauge_degrees=gauge_degrees,
        video_title=video_title,
        slurs_count=slurs_count, policy_flags=policy_flags,
        profanity_count=profanity_count,
        comment_sentiment=comment_sentiment, keywords_html=keywords_html,
        cta_text=cta_text
    )

    temp_html = frames_dir / "reel.html"
    temp_html.write_text(html_content, encoding="utf-8")

    frame_data = []

    section_timings = {
        "sec-header": 0.0,
        "sec-card": 0.3,
        "sec-score": 0.8,
        "sec-flags": 1.5,
        "sec-sentiment": 2.5,
        "sec-keywords": 3.2,
        "sec-cta": 5.0,
        "sec-footer": 5.5,
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1080, "height": 1920})
        page.goto(f"file:///{temp_html.resolve()}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        for frame_idx in range(total_frames):
            t = frame_idx / fps

            for section_id, show_time in section_timings.items():
                if t >= show_time:
                    page.evaluate(f"document.getElementById('{section_id}').classList.add('visible');")
                else:
                    page.evaluate(f"document.getElementById('{section_id}').classList.remove('visible');")

            page.wait_for_timeout(30)

            frame_path = frames_dir / f"frame_{frame_idx:04d}.png"
            page.screenshot(path=str(frame_path), full_page=False)
            frame_data.append({
                "path": str(frame_path),
                "duration": 1.0 / fps
            })

        page.close()
        browser.close()

    print(f"  Rendered {len(frame_data)} frames")

    sfx_dir = output_dir / "sfx"
    sfx_dir.mkdir(parents=True, exist_ok=True)
    click_path = str(sfx_dir / "click.wav")
    create_sfx_wav(click_path)

    print("  Compositing video with moviepy...")

    video_clips = []
    for fd in frame_data:
        img_clip = ImageClip(fd["path"]).with_duration(fd["duration"])
        video_clips.append(img_clip)

    final_video = concatenate_videoclips(video_clips, method="compose")

    reel_path = str(output_dir / "safesponsor_reel.mp4")
    final_video.write_videofile(
        reel_path,
        fps=fps,
        codec="libx264",
        audio=False,
        logger=None,
    )

    for clip in video_clips:
        clip.close()
    final_video.close()

    print(f"  Reel saved: {reel_path}")

    for fd in frame_data:
        if os.path.exists(fd["path"]):
            os.remove(fd["path"])

    return {"reel": reel_path, "sfx_click": click_path}
